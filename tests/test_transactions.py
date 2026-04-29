from datetime import datetime, timezone

import pytest

from src.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    RecordNotFoundError,
    ValidationError,
)
from src.models.account import Account
from src.models.transaction import (
    BaseTransaction,
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)


def create_accounts():
    return {
        "cash": Account("cash", "Cash Wallet", "cash", balance=100),
        "bank": Account("bank", "Bank Account", "bank", balance=500),
    }


def test_base_transaction_is_abstract():
    with pytest.raises(TypeError):
        BaseTransaction(
            transaction_id="tx-1",
            amount=100,
            account_id="cash",
            category="Salary",
        )


def test_income_transaction_apply_and_revert():
    accounts = create_accounts()
    transaction = IncomeTransaction(
        transaction_id="tx-1",
        amount=200,
        account_id="cash",
        category="Salary",
        description="Monthly salary",
    )

    transaction.apply(accounts)
    assert accounts["cash"].balance == 300

    transaction.revert(accounts)
    assert accounts["cash"].balance == 100


def test_expense_transaction_apply_and_revert():
    accounts = create_accounts()
    transaction = ExpenseTransaction(
        transaction_id="tx-1",
        amount=40,
        account_id="cash",
        category="Food",
        description="Dinner",
    )

    transaction.apply(accounts)
    assert accounts["cash"].balance == 60

    transaction.revert(accounts)
    assert accounts["cash"].balance == 100


def test_transfer_transaction_apply_and_revert():
    accounts = create_accounts()
    transaction = TransferTransaction(
        transaction_id="tx-1",
        amount=80,
        source_account_id="bank",
        target_account_id="cash",
        category="Transfer",
        description="ATM withdrawal",
    )

    transaction.apply(accounts)
    assert accounts["bank"].balance == 420
    assert accounts["cash"].balance == 180

    transaction.revert(accounts)
    assert accounts["bank"].balance == 500
    assert accounts["cash"].balance == 100


def test_transactions_share_polymorphic_apply_and_revert_interface():
    accounts = create_accounts()
    transactions = [
        IncomeTransaction("income-1", 50, "cash", "Salary"),
        ExpenseTransaction("expense-1", 20, "cash", "Food"),
        TransferTransaction("transfer-1", 30, "bank", "cash", "Transfer"),
    ]

    for transaction in transactions:
        transaction.apply(accounts)

    assert accounts["cash"].balance == 160
    assert accounts["bank"].balance == 470

    for transaction in reversed(transactions):
        transaction.revert(accounts)

    assert accounts["cash"].balance == 100
    assert accounts["bank"].balance == 500


@pytest.mark.parametrize(
    "transaction_class,args",
    [
        (IncomeTransaction, ("tx-1", 0, "cash", "Salary")),
        (ExpenseTransaction, ("tx-1", -1, "cash", "Food")),
        (TransferTransaction, ("tx-1", 0, "bank", "cash", "Transfer")),
    ],
)
def test_transactions_reject_invalid_amount(transaction_class, args):
    with pytest.raises(InvalidAmountError):
        transaction_class(*args)


def test_income_transaction_rejects_missing_account():
    transaction = IncomeTransaction("tx-1", 100, "missing", "Salary")

    with pytest.raises(RecordNotFoundError):
        transaction.apply(create_accounts())


def test_expense_transaction_rejects_insufficient_funds():
    transaction = ExpenseTransaction("tx-1", 101, "cash", "Food")

    with pytest.raises(InsufficientFundsError):
        transaction.apply(create_accounts())


def test_transfer_transaction_checks_target_before_withdrawing_source():
    accounts = create_accounts()
    transaction = TransferTransaction("tx-1", 80, "bank", "missing", "Transfer")

    with pytest.raises(RecordNotFoundError):
        transaction.apply(accounts)

    assert accounts["bank"].balance == 500


def test_transfer_transaction_rejects_insufficient_source_funds():
    accounts = create_accounts()
    transaction = TransferTransaction("tx-1", 501, "bank", "cash", "Transfer")

    with pytest.raises(InsufficientFundsError):
        transaction.apply(accounts)

    assert accounts["bank"].balance == 500
    assert accounts["cash"].balance == 100


def test_income_transaction_to_dict_returns_common_fields():
    date = datetime(2026, 4, 29, 12, 0, tzinfo=timezone.utc)
    transaction = IncomeTransaction(
        transaction_id="tx-1",
        amount=200,
        account_id="cash",
        category="Salary",
        description="Monthly salary",
        date=date,
    )

    result = transaction.to_dict()

    assert result == {
        "id": "tx-1",
        "created_at": transaction.created_at.isoformat(),
        "updated_at": transaction.updated_at.isoformat(),
        "type": "income",
        "transaction_id": "tx-1",
        "amount": 200,
        "date": date.isoformat(),
        "category": "Salary",
        "description": "Monthly salary",
        "account_id": "cash",
    }


def test_transfer_transaction_to_dict_returns_transfer_fields():
    transaction = TransferTransaction("tx-1", 80, "bank", "cash", "Transfer")
    result = transaction.to_dict()

    assert result["type"] == "transfer"
    assert result["account_id"] == "bank"
    assert result["source_account_id"] == "bank"
    assert result["target_account_id"] == "cash"


@pytest.mark.parametrize(
    "transaction",
    [
        IncomeTransaction("income-1", 50, "cash", "Salary"),
        ExpenseTransaction("expense-1", 20, "cash", "Food"),
        TransferTransaction("transfer-1", 30, "bank", "cash", "Transfer"),
    ],
)
def test_from_dict_restores_transaction_subclasses(transaction):
    restored = BaseTransaction.from_dict(transaction.to_dict())

    assert type(restored) is type(transaction)
    assert restored.id == transaction.id
    assert restored.transaction_id == transaction.transaction_id
    assert restored.amount == transaction.amount
    assert restored.date == transaction.date
    assert restored.category == transaction.category
    assert restored.description == transaction.description
    assert restored.account_id == transaction.account_id
    assert restored.created_at == transaction.created_at
    assert restored.updated_at == transaction.updated_at


@pytest.mark.parametrize(
    "transaction",
    [
        IncomeTransaction("income-1", 50, "cash", "Salary"),
        ExpenseTransaction("expense-1", 20, "cash", "Food"),
    ],
)
def test_specific_transaction_from_dict_restores_common_fields(transaction):
    restored = type(transaction).from_dict(transaction.to_dict())

    assert type(restored) is type(transaction)
    assert restored.transaction_id == transaction.transaction_id
    assert restored.amount == transaction.amount
    assert restored.account_id == transaction.account_id


def test_transfer_from_dict_restores_transfer_fields():
    transaction = TransferTransaction("transfer-1", 30, "bank", "cash", "Transfer")
    restored = TransferTransaction.from_dict(transaction.to_dict())

    assert restored.source_account_id == "bank"
    assert restored.target_account_id == "cash"


def test_from_dict_rejects_unknown_transaction_type():
    with pytest.raises(ValidationError):
        BaseTransaction.from_dict({"type": "unknown"})
