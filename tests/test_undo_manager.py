import pytest

from src.data_structures.stack import Stack
from src.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from src.managers.account_manager import AccountManager
from src.managers.transaction_manager import TransactionManager
from src.managers.undo_manager import UndoManager
from src.models.transaction import (
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)


def create_transaction_manager():
    account_manager = AccountManager()
    account_manager.create_account("cash", "Cash Wallet", "cash", balance=100)
    account_manager.create_account("bank", "Bank Account", "bank", balance=500)
    return TransactionManager(account_manager)


def create_undo_manager():
    return UndoManager(create_transaction_manager())


def add_and_record(undo_manager, transaction):
    undo_manager.transaction_manager.add_transaction(transaction)
    undo_manager.record_add_transaction(transaction)
    return transaction


def test_undo_manager_uses_stack():
    undo_manager = create_undo_manager()

    assert isinstance(undo_manager.history, Stack)


def test_record_add_transaction_increases_history_size():
    undo_manager = create_undo_manager()
    transaction = add_and_record(
        undo_manager,
        IncomeTransaction("tx-1", 50, "cash", "salary"),
    )

    assert undo_manager.history_size() == 1
    assert undo_manager.has_history() is True
    assert undo_manager.history.peek() == {
        "action": "add_transaction",
        "transaction_id": transaction.transaction_id,
    }


def test_undo_last_reverts_added_income_transaction():
    undo_manager = create_undo_manager()
    transaction = add_and_record(
        undo_manager,
        IncomeTransaction("tx-1", 50, "cash", "salary"),
    )

    undone = undo_manager.undo_last()

    assert undone is transaction
    assert undo_manager.transaction_manager.account_manager.get_account("cash").balance == 100
    assert undo_manager.has_history() is False
    with pytest.raises(RecordNotFoundError):
        undo_manager.transaction_manager.get_transaction("tx-1")


def test_undo_last_reverts_added_expense_transaction():
    undo_manager = create_undo_manager()
    transaction = add_and_record(
        undo_manager,
        ExpenseTransaction("tx-1", 40, "cash", "food"),
    )

    undone = undo_manager.undo_last()

    assert undone is transaction
    assert undo_manager.transaction_manager.account_manager.get_account("cash").balance == 100


def test_undo_last_reverts_added_transfer_transaction():
    undo_manager = create_undo_manager()
    transaction = add_and_record(
        undo_manager,
        TransferTransaction("tx-1", 80, "bank", "cash", "transfer"),
    )

    undone = undo_manager.undo_last()

    assert undone is transaction
    assert undo_manager.transaction_manager.account_manager.get_account("bank").balance == 500
    assert undo_manager.transaction_manager.account_manager.get_account("cash").balance == 100


def test_undo_last_uses_lifo_order():
    undo_manager = create_undo_manager()
    first = add_and_record(undo_manager, IncomeTransaction("tx-1", 50, "cash", "salary"))
    second = add_and_record(undo_manager, ExpenseTransaction("tx-2", 20, "cash", "food"))

    assert undo_manager.undo_last() is second
    assert undo_manager.transaction_manager.account_manager.get_account("cash").balance == 150
    assert undo_manager.undo_last() is first
    assert undo_manager.transaction_manager.account_manager.get_account("cash").balance == 100


def test_undo_last_returns_none_when_history_empty():
    undo_manager = create_undo_manager()

    assert undo_manager.undo_last() is None
    assert undo_manager.has_history() is False
    assert undo_manager.history_size() == 0


def test_failed_add_transaction_is_not_recorded():
    undo_manager = create_undo_manager()
    undo_manager.transaction_manager.add_transaction(
        IncomeTransaction("tx-1", 50, "cash", "salary")
    )

    with pytest.raises(DuplicateRecordError):
        undo_manager.transaction_manager.add_transaction(
            ExpenseTransaction("tx-1", 20, "cash", "food")
        )

    assert undo_manager.has_history() is False
    assert undo_manager.history_size() == 0


def test_undo_missing_transaction_raises_record_not_found():
    undo_manager = create_undo_manager()
    transaction = add_and_record(
        undo_manager,
        IncomeTransaction("tx-1", 50, "cash", "salary"),
    )
    undo_manager.transaction_manager.delete_transaction(transaction.transaction_id)

    with pytest.raises(RecordNotFoundError):
        undo_manager.undo_last()


def test_undo_rejects_unsupported_action():
    undo_manager = create_undo_manager()
    undo_manager.history.push({"action": "unknown", "transaction_id": "tx-1"})

    with pytest.raises(ValidationError):
        undo_manager.undo_last()
