from abc import ABC, abstractmethod
from datetime import datetime, timezone

from src.exceptions import InvalidAmountError, RecordNotFoundError, ValidationError
from src.models.base import BaseRecord


class BaseTransaction(BaseRecord, ABC):
    transaction_type = None

    def __init__(
        self,
        transaction_id,
        amount,
        account_id,
        category,
        description="",
        date=None,
    ):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive")

        super().__init__(record_id=transaction_id)
        self.transaction_id = transaction_id
        self.amount = amount
        self.account_id = account_id
        self.category = category
        self.description = description
        self.date = date or datetime.now(timezone.utc)

    @abstractmethod
    def apply(self, accounts):
        pass

    @abstractmethod
    def revert(self, accounts):
        pass

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "type": self.transaction_type,
                "transaction_id": self.transaction_id,
                "amount": self.amount,
                "date": self.date.isoformat(),
                "category": self.category,
                "description": self.description,
                "account_id": self.account_id,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data):
        transaction_type = data["type"]
        transaction_classes = {
            IncomeTransaction.transaction_type: IncomeTransaction,
            ExpenseTransaction.transaction_type: ExpenseTransaction,
            TransferTransaction.transaction_type: TransferTransaction,
        }

        transaction_class = transaction_classes.get(transaction_type)
        if transaction_class is None:
            raise ValidationError("Unknown transaction type")

        return transaction_class.from_dict(data)

    @staticmethod
    def _get_account(accounts, account_id):
        account = accounts.get(account_id)
        if account is None:
            raise RecordNotFoundError(f"Account not found: {account_id}")
        return account

    def _restore_record_fields(self, data):
        self.created_at = datetime.fromisoformat(data["created_at"])
        self.updated_at = datetime.fromisoformat(data["updated_at"])


class IncomeTransaction(BaseTransaction):
    transaction_type = "income"

    def apply(self, accounts):
        account = self._get_account(accounts, self.account_id)
        account.deposit(self.amount)

    def revert(self, accounts):
        account = self._get_account(accounts, self.account_id)
        account.withdraw(self.amount)

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            transaction_id=data["transaction_id"],
            amount=data["amount"],
            account_id=data["account_id"],
            category=data["category"],
            description=data.get("description", ""),
            date=datetime.fromisoformat(data["date"]),
        )
        transaction._restore_record_fields(data)
        return transaction


class ExpenseTransaction(BaseTransaction):
    transaction_type = "expense"

    def apply(self, accounts):
        account = self._get_account(accounts, self.account_id)
        account.withdraw(self.amount)

    def revert(self, accounts):
        account = self._get_account(accounts, self.account_id)
        account.deposit(self.amount)

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            transaction_id=data["transaction_id"],
            amount=data["amount"],
            account_id=data["account_id"],
            category=data["category"],
            description=data.get("description", ""),
            date=datetime.fromisoformat(data["date"]),
        )
        transaction._restore_record_fields(data)
        return transaction


class TransferTransaction(BaseTransaction):
    transaction_type = "transfer"

    def __init__(
        self,
        transaction_id,
        amount,
        source_account_id,
        target_account_id,
        category,
        description="",
        date=None,
    ):
        super().__init__(
            transaction_id=transaction_id,
            amount=amount,
            account_id=source_account_id,
            category=category,
            description=description,
            date=date,
        )
        self.source_account_id = source_account_id
        self.target_account_id = target_account_id

    def apply(self, accounts):
        source_account = self._get_account(accounts, self.source_account_id)
        target_account = self._get_account(accounts, self.target_account_id)

        source_account.withdraw(self.amount)
        target_account.deposit(self.amount)

    def revert(self, accounts):
        source_account = self._get_account(accounts, self.source_account_id)
        target_account = self._get_account(accounts, self.target_account_id)

        target_account.withdraw(self.amount)
        source_account.deposit(self.amount)

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "source_account_id": self.source_account_id,
                "target_account_id": self.target_account_id,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            transaction_id=data["transaction_id"],
            amount=data["amount"],
            source_account_id=data["source_account_id"],
            target_account_id=data["target_account_id"],
            category=data["category"],
            description=data.get("description", ""),
            date=datetime.fromisoformat(data["date"]),
        )
        transaction._restore_record_fields(data)
        return transaction
