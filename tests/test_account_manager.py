import pytest

from src.data_structures.hash_table import HashTable
from src.exceptions import DuplicateRecordError, InvalidAmountError, RecordNotFoundError
from src.managers.account_manager import AccountManager
from src.models.account import Account


def test_account_manager_uses_hash_table():
    manager = AccountManager()

    assert isinstance(manager.accounts, HashTable)


def test_create_account_and_get_by_id():
    manager = AccountManager()

    account = manager.create_account(
        account_id="acc-1",
        name="Cash Wallet",
        account_type="cash",
        balance=100,
        currency="USD",
    )

    assert isinstance(account, Account)
    assert manager.get_account("acc-1") is account
    assert account.account_id == "acc-1"
    assert account.balance == 100


def test_create_account_rejects_duplicate_id():
    manager = AccountManager()
    manager.create_account("acc-1", "Cash Wallet", "cash")

    with pytest.raises(DuplicateRecordError):
        manager.create_account("acc-1", "Bank Account", "bank")


def test_get_account_rejects_unknown_id():
    manager = AccountManager()

    with pytest.raises(RecordNotFoundError):
        manager.get_account("missing")


def test_update_account_updates_given_fields():
    manager = AccountManager()
    account = manager.create_account("acc-1", "Cash Wallet", "cash", balance=100)
    old_updated_at = account.updated_at

    updated = manager.update_account(
        account_id="acc-1",
        name="Daily Cash",
        account_type="wallet",
        balance=150,
        currency="CNY",
    )

    assert updated is account
    assert updated.name == "Daily Cash"
    assert updated.account_type == "wallet"
    assert updated.balance == 150
    assert updated.currency == "CNY"
    assert updated.updated_at > old_updated_at


def test_update_account_preserves_omitted_fields():
    manager = AccountManager()
    account = manager.create_account(
        "acc-1",
        "Cash Wallet",
        "cash",
        balance=100,
        currency="USD",
    )

    manager.update_account("acc-1", name="Daily Cash")

    assert account.name == "Daily Cash"
    assert account.account_type == "cash"
    assert account.balance == 100
    assert account.currency == "USD"


def test_update_account_rejects_unknown_id():
    manager = AccountManager()

    with pytest.raises(RecordNotFoundError):
        manager.update_account("missing", name="Unknown")


def test_update_account_rejects_negative_balance():
    manager = AccountManager()
    manager.create_account("acc-1", "Cash Wallet", "cash", balance=100)

    with pytest.raises(InvalidAmountError):
        manager.update_account("acc-1", balance=-1)


def test_delete_account_removes_and_returns_account():
    manager = AccountManager()
    account = manager.create_account("acc-1", "Cash Wallet", "cash")

    deleted = manager.delete_account("acc-1")

    assert deleted is account
    with pytest.raises(RecordNotFoundError):
        manager.get_account("acc-1")


def test_delete_account_rejects_unknown_id():
    manager = AccountManager()

    with pytest.raises(RecordNotFoundError):
        manager.delete_account("missing")


def test_list_accounts_returns_all_accounts():
    manager = AccountManager()
    cash = manager.create_account("acc-1", "Cash Wallet", "cash")
    bank = manager.create_account("acc-2", "Bank Account", "bank")

    accounts = manager.list_accounts()

    assert set(accounts) == {cash, bank}
