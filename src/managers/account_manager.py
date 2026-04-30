from src.data_structures.hash_table import HashTable
from src.exceptions import DuplicateRecordError, InvalidAmountError, RecordNotFoundError
from src.models.account import Account


class AccountManager:
    def __init__(self):
        self.accounts = HashTable()

    def create_account(
        self,
        account_id,
        name,
        account_type,
        balance=0,
        currency="USD",
    ):
        if self.accounts.contains(account_id):
            raise DuplicateRecordError(f"Account already exists: {account_id}")

        account = Account(
            account_id=account_id,
            name=name,
            account_type=account_type,
            balance=balance,
            currency=currency,
        )
        self.accounts.put(account_id, account)
        return account

    def get_account(self, account_id):
        account = self.accounts.get(account_id)
        if account is None:
            raise RecordNotFoundError(f"Account not found: {account_id}")
        return account

    def update_account(
        self,
        account_id,
        name=None,
        account_type=None,
        balance=None,
        currency=None,
    ):
        account = self.get_account(account_id)

        if name is not None:
            account.rename(name)
        if account_type is not None:
            account.account_type = account_type
        if balance is not None:
            if balance < 0:
                raise InvalidAmountError("Balance cannot be negative")
            account.balance = balance
        if currency is not None:
            account.currency = currency

        if account_type is not None or balance is not None or currency is not None:
            account.touch()

        return account

    def delete_account(self, account_id):
        if not self.accounts.contains(account_id):
            raise RecordNotFoundError(f"Account not found: {account_id}")
        return self.accounts.remove(account_id)

    def list_accounts(self):
        accounts = []
        for bucket in self.accounts.table:
            for _, account in bucket:
                accounts.append(account)
        return accounts
