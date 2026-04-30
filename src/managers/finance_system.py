from src.managers.account_manager import AccountManager
from src.managers.audit_manager import AuditManager
from src.managers.category_manager import CategoryManager
from src.managers.pending_transaction_manager import PendingTransactionManager
from src.managers.transaction_manager import TransactionManager
from src.managers.undo_manager import UndoManager
from src.models.budget import Budget
from src.models.transaction import (
    ExpenseTransaction,
    IncomeTransaction,
    TransferTransaction,
)
from src.storage.json_storage import JsonStorage


class FinanceSystem:
    def __init__(self, storage=None):
        self.storage = storage or JsonStorage()
        self.account_manager = AccountManager()
        self.transaction_manager = TransactionManager(self.account_manager)
        self.category_manager = CategoryManager(self.transaction_manager)
        self.audit_manager = AuditManager()
        self.pending_manager = PendingTransactionManager(self.transaction_manager)
        self.undo_manager = UndoManager(self.transaction_manager)
        self.budgets = []

    def create_account(
        self,
        account_id,
        name,
        account_type,
        balance=0,
        currency="USD",
    ):
        account = self.account_manager.create_account(
            account_id=account_id,
            name=name,
            account_type=account_type,
            balance=balance,
            currency=currency,
        )
        self.audit_manager.add_block(
            "create_account",
            account_id,
            {
                "name": name,
                "account_type": account_type,
                "balance": balance,
                "currency": currency,
            },
        )
        return account

    def get_account(self, account_id):
        return self.account_manager.get_account(account_id)

    def list_accounts(self):
        return self.account_manager.list_accounts()

    def add_income_transaction(
        self,
        transaction_id,
        amount,
        account_id,
        category,
        description="",
        date=None,
    ):
        transaction = IncomeTransaction(
            transaction_id=transaction_id,
            amount=amount,
            account_id=account_id,
            category=category,
            description=description,
            date=date,
        )
        return self._add_transaction(transaction)

    def add_expense_transaction(
        self,
        transaction_id,
        amount,
        account_id,
        category,
        description="",
        date=None,
    ):
        transaction = ExpenseTransaction(
            transaction_id=transaction_id,
            amount=amount,
            account_id=account_id,
            category=category,
            description=description,
            date=date,
        )
        return self._add_transaction(transaction)

    def add_transfer_transaction(
        self,
        transaction_id,
        amount,
        source_account_id,
        target_account_id,
        category,
        description="",
        date=None,
    ):
        transaction = TransferTransaction(
            transaction_id=transaction_id,
            amount=amount,
            source_account_id=source_account_id,
            target_account_id=target_account_id,
            category=category,
            description=description,
            date=date,
        )
        return self._add_transaction(transaction)

    def get_transaction(self, transaction_id):
        return self.transaction_manager.get_transaction(transaction_id)

    def list_transactions(self):
        return self.transaction_manager.list_transactions()

    def search_transactions_by_amount(self, minimum, maximum):
        return self.transaction_manager.search_by_amount_range(minimum, maximum)

    def create_category(self, category_id, name, parent_id=None):
        category = self.category_manager.create_category(category_id, name, parent_id)
        self.audit_manager.add_block(
            "create_category",
            category_id,
            category.to_dict(),
        )
        return category

    def find_category(self, category_id):
        return self.category_manager.find_category(category_id)

    def list_categories(self):
        return self.category_manager.list_categories()

    def calculate_category_spending(self, category_id):
        return self.category_manager.calculate_category_spending(category_id)

    def add_budget(self, budget):
        self.budgets.append(budget)
        self.audit_manager.add_block(
            "create_budget",
            budget.budget_id,
            budget.to_dict(),
        )
        return budget

    def create_budget(
        self,
        budget_id,
        category_id,
        period,
        limit_amount,
        spent_amount=0.0,
    ):
        return self.add_budget(
            Budget(
                budget_id=budget_id,
                category_id=category_id,
                period=period,
                limit_amount=limit_amount,
                spent_amount=spent_amount,
            )
        )

    def list_budgets(self):
        return list(self.budgets)

    def enqueue_pending_transaction(self, transaction):
        return self.pending_manager.enqueue_transaction(transaction)

    def process_next_pending(self):
        transaction = self.pending_manager.process_next()
        if transaction is not None:
            self.undo_manager.record_add_transaction(transaction)
            self.audit_manager.add_block(
                "process_pending_transaction",
                transaction.transaction_id,
                transaction.to_dict(),
            )
        return transaction

    def undo_last(self):
        transaction = self.undo_manager.undo_last()
        if transaction is not None:
            self.audit_manager.add_block(
                "undo_transaction",
                transaction.transaction_id,
                {
                    "transaction_id": transaction.transaction_id,
                    "amount": transaction.amount,
                },
            )
        return transaction

    def validate_audit_chain(self):
        return self.audit_manager.validate_chain()

    def save(self):
        self.storage.save(
            self.account_manager,
            self.transaction_manager,
            self.category_manager,
            self.budgets,
            self.audit_manager,
        )

    def load(self):
        state = self.storage.load()
        self.account_manager = state["account_manager"]
        self.transaction_manager = state["transaction_manager"]
        self.category_manager = state["category_manager"]
        self.budgets = state["budgets"]
        self.audit_manager = state["audit_manager"]
        self.pending_manager = PendingTransactionManager(self.transaction_manager)
        self.undo_manager = UndoManager(self.transaction_manager)
        return self

    def _add_transaction(self, transaction):
        added = self.transaction_manager.add_transaction(transaction)
        self.undo_manager.record_add_transaction(added)
        self.audit_manager.add_block(
            "create_transaction",
            added.transaction_id,
            added.to_dict(),
        )
        return added
