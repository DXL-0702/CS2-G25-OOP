import pytest

from src.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    RecordNotFoundError,
    ValidationError,
)
from src.managers import (
    AccountManager,
    AuditManager,
    CategoryManager,
    FinanceSystem,
    PendingTransactionManager,
    TransactionManager,
    UndoManager,
)
from src.models.transaction import ExpenseTransaction
from src.storage.json_storage import JsonStorage


def create_system(tmp_path):
    return FinanceSystem(JsonStorage(tmp_path / "system_state.json"))


def test_finance_system_initializes_managers(tmp_path):
    system = create_system(tmp_path)

    assert isinstance(system.account_manager, AccountManager)
    assert isinstance(system.transaction_manager, TransactionManager)
    assert isinstance(system.category_manager, CategoryManager)
    assert isinstance(system.audit_manager, AuditManager)
    assert isinstance(system.pending_manager, PendingTransactionManager)
    assert isinstance(system.undo_manager, UndoManager)
    assert system.budgets == []


def test_create_account_writes_audit_log(tmp_path):
    system = create_system(tmp_path)

    account = system.create_account("cash", "Cash Wallet", "cash", balance=100)

    assert system.get_account("cash") is account
    assert len(system.audit_manager.list_blocks()) == 1
    assert system.audit_manager.list_blocks()[0].operation_type == "create_account"
    assert system.validate_audit_chain() is True


def test_add_transactions_update_balances_and_can_be_queried(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.create_account("bank", "Bank Account", "bank", balance=500)

    income = system.add_income_transaction("tx-1", 50, "cash", "salary")
    expense = system.add_expense_transaction("tx-2", 20, "cash", "food")
    transfer = system.add_transfer_transaction("tx-3", 100, "bank", "cash", "transfer")

    assert system.get_account("cash").balance == 230
    assert system.get_account("bank").balance == 400
    assert system.get_transaction("tx-1") is income
    assert system.search_transactions_by_amount(10, 60) == [expense, income]
    assert set(system.list_transactions()) == {income, expense, transfer}
    assert system.validate_audit_chain() is True


def test_category_spending_and_budget_flow(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.create_category("food", "Food")
    system.create_category("restaurant", "Restaurant", parent_id="food")
    budget = system.create_budget("budget-1", "food", "2026-05", 300, spent_amount=40)

    system.add_expense_transaction("tx-1", 40, "cash", "restaurant")

    assert system.calculate_category_spending("food") == 40
    assert system.list_budgets() == [budget]
    assert system.validate_audit_chain() is True


def test_pending_transaction_processing_and_undo(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    pending = ExpenseTransaction("tx-1", 40, "cash", "food")

    system.enqueue_pending_transaction(pending)
    processed = system.process_next_pending()

    assert processed is pending
    assert system.get_account("cash").balance == 60
    assert system.pending_manager.peek_next() is None

    undone = system.undo_last()

    assert undone is pending
    assert system.get_account("cash").balance == 100
    assert system.validate_audit_chain() is True


def test_empty_pending_and_empty_undo_do_not_write_audit(tmp_path):
    system = create_system(tmp_path)
    initial_audit_count = len(system.audit_manager.list_blocks())

    assert system.process_next_pending() is None
    assert system.undo_last() is None

    assert len(system.audit_manager.list_blocks()) == initial_audit_count


def test_save_and_load_restores_system_state(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    system = FinanceSystem(storage)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.create_account("bank", "Bank Account", "bank", balance=500)
    system.create_category("food", "Food")
    system.create_category("restaurant", "Restaurant", parent_id="food")
    system.create_budget("budget-1", "food", "2026-05", 300, spent_amount=40)
    system.add_expense_transaction("tx-1", 40, "cash", "restaurant")
    system.save()

    loaded_system = FinanceSystem(storage).load()

    assert loaded_system.get_account("cash").balance == 60
    assert loaded_system.get_transaction("tx-1").amount == 40
    assert loaded_system.calculate_category_spending("food") == 40
    assert loaded_system.list_budgets()[0].budget_id == "budget-1"
    assert loaded_system.validate_audit_chain() is True
    assert loaded_system.pending_manager.transaction_manager is loaded_system.transaction_manager
    assert loaded_system.undo_manager.transaction_manager is loaded_system.transaction_manager


def test_finance_system_update_and_delete_account_write_audit(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)

    updated = system.update_account("cash", name="Daily Cash", balance=150)
    deleted = system.delete_account("cash")

    assert updated.name == "Daily Cash"
    assert deleted.account_id == "cash"
    assert [block.operation_type for block in system.list_audit_blocks()] == [
        "create_account",
        "update_account",
        "delete_account",
    ]
    assert system.validate_audit_chain() is True


def test_finance_system_update_and_delete_transaction_write_audit(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.add_expense_transaction("tx-1", 20, "cash", "food")

    updated = system.update_transaction("tx-1", amount=40)
    deleted = system.delete_transaction("tx-1")

    assert updated.amount == 40
    assert deleted.transaction_id == "tx-1"
    assert system.get_account("cash").balance == 100
    assert [block.operation_type for block in system.list_audit_blocks()] == [
        "create_account",
        "create_transaction",
        "update_transaction",
        "delete_transaction",
    ]
    assert system.validate_audit_chain() is True


def test_finance_system_pending_wrappers(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)

    pending = system.create_pending_income_transaction("tx-1", 50, "cash", "salary")

    assert system.peek_pending_transaction() is pending
    assert system.list_pending_transactions() == [pending]


def test_finance_system_rejects_negative_account_balance_without_audit(tmp_path):
    system = create_system(tmp_path)

    with pytest.raises(InvalidAmountError):
        system.create_account("bad", "Bad Account", "cash", balance=-1)

    assert system.list_accounts() == []
    assert system.list_audit_blocks() == []


@pytest.mark.parametrize(
    "operation",
    [
        lambda system: system.add_income_transaction("tx-1", 0, "cash", "salary"),
        lambda system: system.add_expense_transaction("tx-1", -10, "cash", "food"),
        lambda system: system.add_transfer_transaction("tx-1", 0, "cash", "bank", "transfer"),
    ],
)
def test_finance_system_rejects_non_positive_transactions_without_state_change(tmp_path, operation):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.create_account("bank", "Bank Account", "bank", balance=500)

    with pytest.raises(InvalidAmountError):
        operation(system)

    assert system.get_account("cash").balance == 100
    assert system.get_account("bank").balance == 500
    assert system.list_transactions() == []
    assert [block.operation_type for block in system.list_audit_blocks()] == [
        "create_account",
        "create_account",
    ]


def test_finance_system_rejects_insufficient_funds_without_state_change(tmp_path):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)
    system.create_account("bank", "Bank Account", "bank", balance=50)

    with pytest.raises(InsufficientFundsError):
        system.add_expense_transaction("tx-1", 150, "cash", "food")
    with pytest.raises(InsufficientFundsError):
        system.add_transfer_transaction("tx-2", 80, "bank", "cash", "transfer")

    assert system.get_account("cash").balance == 100
    assert system.get_account("bank").balance == 50
    assert system.list_transactions() == []


@pytest.mark.parametrize(
    "operation",
    [
        lambda system: system.add_income_transaction("tx-1", 50, "missing", "salary"),
        lambda system: system.add_expense_transaction("tx-1", 20, "missing", "food"),
        lambda system: system.add_transfer_transaction("tx-1", 20, "missing", "cash", "transfer"),
        lambda system: system.add_transfer_transaction("tx-1", 20, "cash", "missing", "transfer"),
    ],
)
def test_finance_system_rejects_transactions_with_missing_accounts(tmp_path, operation):
    system = create_system(tmp_path)
    system.create_account("cash", "Cash Wallet", "cash", balance=100)

    with pytest.raises(RecordNotFoundError):
        operation(system)

    assert system.get_account("cash").balance == 100
    assert system.list_transactions() == []


@pytest.mark.parametrize(
    "operation",
    [
        lambda system: system.get_transaction("missing"),
        lambda system: system.update_transaction("missing", amount=20),
        lambda system: system.delete_transaction("missing"),
    ],
)
def test_finance_system_rejects_missing_transaction_operations(tmp_path, operation):
    system = create_system(tmp_path)

    with pytest.raises(RecordNotFoundError):
        operation(system)


@pytest.mark.parametrize(
    "minimum,maximum,expected_error",
    [
        (-1, 100, InvalidAmountError),
        (100, 10, ValidationError),
    ],
)
def test_finance_system_rejects_invalid_amount_ranges(tmp_path, minimum, maximum, expected_error):
    system = create_system(tmp_path)

    with pytest.raises(expected_error):
        system.search_transactions_by_amount(minimum, maximum)
