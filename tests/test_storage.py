import json

import pytest

from src.exceptions import DataStorageError
from src.managers.account_manager import AccountManager
from src.managers.audit_manager import AuditManager
from src.managers.category_manager import CategoryManager
from src.managers.transaction_manager import TransactionManager
from src.models.audit import AuditBlock
from src.models.budget import Budget
from src.models.category import CategoryNode
from src.models.transaction import ExpenseTransaction, IncomeTransaction
from src.storage.json_storage import JsonStorage


def create_sample_state():
    account_manager = AccountManager()
    account_manager.create_account("cash", "Cash Wallet", "cash", balance=500)
    account_manager.create_account("bank", "Bank Account", "bank", balance=1000)

    transaction_manager = TransactionManager(account_manager)
    transaction_manager.add_transaction(
        ExpenseTransaction("tx-1", 40, "cash", "restaurant", "Dinner")
    )
    transaction_manager.add_transaction(
        IncomeTransaction("tx-2", 100, "bank", "salary", "Monthly salary")
    )

    category_manager = CategoryManager(transaction_manager)
    category_manager.create_category("food", "Food")
    category_manager.create_category("restaurant", "Restaurant", parent_id="food")
    category_manager.create_category("income", "Income")
    category_manager.create_category("salary", "Salary", parent_id="income")

    budgets = [Budget("budget-1", "food", "2026-05", 300, 40)]

    audit_manager = AuditManager()
    audit_manager.add_block("create_account", "cash", {"name": "Cash Wallet"})
    audit_manager.add_block("create_transaction", "tx-1", {"amount": 40})

    return account_manager, transaction_manager, category_manager, budgets, audit_manager


def test_storage_reports_missing_file(tmp_path):
    storage = JsonStorage(tmp_path / "data" / "system_state.json")

    assert storage.exists() is False


def test_load_missing_file_returns_empty_state(tmp_path):
    storage = JsonStorage(tmp_path / "data" / "system_state.json")

    state = storage.load()

    assert state["account_manager"].list_accounts() == []
    assert state["transaction_manager"].list_transactions() == []
    assert state["category_manager"].list_categories() == []
    assert state["budgets"] == []
    assert state["audit_manager"].list_blocks() == []
    assert storage.exists() is False


def test_save_creates_parent_directory_and_file(tmp_path):
    storage = JsonStorage(tmp_path / "nested" / "system_state.json")
    state = create_sample_state()

    storage.save(*state)

    assert storage.exists() is True
    assert (tmp_path / "nested" / "system_state.json").exists()


def test_save_and_load_restores_accounts_without_reapplying_transactions(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    account_manager, transaction_manager, category_manager, budgets, audit_manager = create_sample_state()
    original_cash_balance = account_manager.get_account("cash").balance
    original_bank_balance = account_manager.get_account("bank").balance

    storage.save(account_manager, transaction_manager, category_manager, budgets, audit_manager)
    loaded = storage.load()

    loaded_accounts = loaded["account_manager"]
    assert loaded_accounts.get_account("cash").balance == original_cash_balance
    assert loaded_accounts.get_account("bank").balance == original_bank_balance


def test_load_rebuilds_transaction_hash_index_amount_index_and_timeline(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.save(*create_sample_state())

    loaded = storage.load()
    transaction_manager = loaded["transaction_manager"]

    assert transaction_manager.get_transaction("tx-1").amount == 40
    assert transaction_manager.search_by_amount_range(30, 50) == [
        transaction_manager.get_transaction("tx-1")
    ]
    assert [transaction.transaction_id for transaction in transaction_manager.get_timeline()] == [
        "tx-1",
        "tx-2",
    ]


def test_load_rebuilds_category_tree_and_spending(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.save(*create_sample_state())

    loaded = storage.load()
    category_manager = loaded["category_manager"]

    assert category_manager.find_category("restaurant").name == "Restaurant"
    assert [category.category_id for category in category_manager.list_categories()] == [
        "food",
        "restaurant",
        "income",
        "salary",
    ]
    assert category_manager.calculate_category_spending("food") == 40


def test_load_restores_budgets(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.save(*create_sample_state())

    loaded = storage.load()
    budget = loaded["budgets"][0]

    assert budget.budget_id == "budget-1"
    assert budget.category_id == "food"
    assert budget.remaining_amount() == 260
    assert budget.is_over_budget() is False


def test_load_restores_audit_chain(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.save(*create_sample_state())

    loaded = storage.load()
    audit_manager = loaded["audit_manager"]

    assert len(audit_manager.list_blocks()) == 2
    assert audit_manager.validate_chain() is True


def test_tampered_audit_payload_loads_but_fails_validation(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.save(*create_sample_state())
    data = json.loads(storage.file_path.read_text(encoding="utf-8"))
    data["audit_blocks"][0]["payload_summary"]["name"] = "Tampered"
    storage.file_path.write_text(json.dumps(data), encoding="utf-8")

    loaded = storage.load()

    assert loaded["audit_manager"].validate_chain() is False


def test_load_empty_file_raises_data_storage_error(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.file_path.write_text("", encoding="utf-8")

    with pytest.raises(DataStorageError):
        storage.load()


def test_load_invalid_json_raises_data_storage_error(tmp_path):
    storage = JsonStorage(tmp_path / "system_state.json")
    storage.file_path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(DataStorageError):
        storage.load()


def test_category_node_from_dict_restores_children():
    category = CategoryNode.from_dict(
        {
            "category_id": "food",
            "name": "Food",
            "parent_id": None,
            "children": [
                {
                    "category_id": "restaurant",
                    "name": "Restaurant",
                    "parent_id": "food",
                    "children": [],
                }
            ],
        }
    )

    assert category.category_id == "food"
    assert category.children[0].category_id == "restaurant"
    assert category.children[0].parent_id == "food"


def test_audit_block_can_load_from_storage_dict_without_rehashing():
    block = AuditBlock(0, "create_account", "cash", {"name": "Cash"})
    data = block.to_dict()
    data["current_hash"] = "stored-hash"

    restored = AuditBlock.from_dict(data)

    assert restored.current_hash == "stored-hash"
