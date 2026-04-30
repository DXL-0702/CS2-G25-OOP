import json
from pathlib import Path

from src.exceptions import DataStorageError
from src.managers.account_manager import AccountManager
from src.managers.audit_manager import AuditManager
from src.managers.category_manager import CategoryManager
from src.managers.transaction_manager import TransactionManager
from src.models.account import Account
from src.models.audit import AuditBlock
from src.models.budget import Budget
from src.models.transaction import BaseTransaction


class JsonStorage:
    def __init__(self, file_path="data/system_state.json"):
        self.file_path = Path(file_path)

    def exists(self):
        return self.file_path.exists()

    def save(
        self,
        account_manager,
        transaction_manager,
        category_manager,
        budgets,
        audit_manager,
    ):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "version": 1,
            "accounts": [
                account.to_dict()
                for account in account_manager.list_accounts()
            ],
            "transactions": [
                transaction.to_dict()
                for transaction in transaction_manager.get_timeline()
            ],
            "categories": [
                {
                    "category_id": category.category_id,
                    "name": category.name,
                    "parent_id": category.parent_id,
                }
                for category in category_manager.list_categories()
            ],
            "budgets": [budget.to_dict() for budget in budgets],
            "audit_blocks": [
                block.to_dict()
                for block in audit_manager.list_blocks()
            ],
        }
        self.file_path.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )

    def load(self):
        if not self.exists():
            return self._empty_state()

        try:
            raw_data = self.file_path.read_text(encoding="utf-8")
            if not raw_data.strip():
                raise DataStorageError("Storage file is empty")
            data = json.loads(raw_data)
        except DataStorageError:
            raise
        except (OSError, json.JSONDecodeError) as error:
            raise DataStorageError("Failed to load storage file") from error

        try:
            return self._build_state(data)
        except (KeyError, TypeError, ValueError) as error:
            raise DataStorageError("Invalid storage data") from error

    def _empty_state(self):
        account_manager = AccountManager()
        transaction_manager = TransactionManager(account_manager)
        category_manager = CategoryManager(transaction_manager)
        return {
            "account_manager": account_manager,
            "transaction_manager": transaction_manager,
            "category_manager": category_manager,
            "budgets": [],
            "audit_manager": AuditManager(),
        }

    def _build_state(self, data):
        account_manager = AccountManager()
        for account_data in data.get("accounts", []):
            account = Account.from_dict(account_data)
            account_manager.accounts.put(account.account_id, account)

        transaction_manager = TransactionManager(account_manager)
        for transaction_data in data.get("transactions", []):
            transaction = BaseTransaction.from_dict(transaction_data)
            transaction_manager._store_transaction(transaction)

        category_manager = CategoryManager(transaction_manager)
        self._load_categories(category_manager, data.get("categories", []))

        audit_manager = AuditManager()
        for block_data in data.get("audit_blocks", []):
            audit_manager.blocks.append(AuditBlock.from_dict(block_data))

        return {
            "account_manager": account_manager,
            "transaction_manager": transaction_manager,
            "category_manager": category_manager,
            "budgets": [
                Budget.from_dict(budget_data)
                for budget_data in data.get("budgets", [])
            ],
            "audit_manager": audit_manager,
        }

    def _load_categories(self, category_manager, category_data_list):
        pending_categories = list(category_data_list)
        while pending_categories:
            remaining = []
            loaded_any = False
            for category_data in pending_categories:
                parent_id = category_data.get("parent_id")
                if parent_id is None or parent_id in category_manager.categories:
                    category_manager.create_category(
                        category_id=category_data["category_id"],
                        name=category_data["name"],
                        parent_id=parent_id,
                    )
                    loaded_any = True
                else:
                    remaining.append(category_data)

            if not loaded_any:
                raise DataStorageError("Category parent is missing")
            pending_categories = remaining
