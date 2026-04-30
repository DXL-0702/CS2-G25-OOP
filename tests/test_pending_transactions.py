import pytest

from src.data_structures.queue import Queue
from src.exceptions import DuplicateRecordError, InsufficientFundsError
from src.managers.account_manager import AccountManager
from src.managers.pending_transaction_manager import PendingTransactionManager
from src.managers.transaction_manager import TransactionManager
from src.models.transaction import ExpenseTransaction, IncomeTransaction


def create_transaction_manager():
    account_manager = AccountManager()
    account_manager.create_account("cash", "Cash Wallet", "cash", balance=100)
    return TransactionManager(account_manager)


def create_pending_manager():
    return PendingTransactionManager(create_transaction_manager())


def test_pending_manager_uses_queue():
    manager = create_pending_manager()

    assert isinstance(manager.pending_queue, Queue)


def test_enqueue_transaction_then_peek_next():
    manager = create_pending_manager()
    transaction = IncomeTransaction("tx-1", 50, "cash", "salary")

    enqueued = manager.enqueue_transaction(transaction)

    assert enqueued is transaction
    assert manager.peek_next() is transaction


def test_list_pending_returns_fifo_order():
    manager = create_pending_manager()
    first = manager.enqueue_transaction(IncomeTransaction("tx-1", 50, "cash", "salary"))
    second = manager.enqueue_transaction(ExpenseTransaction("tx-2", 20, "cash", "food"))

    assert manager.list_pending() == [first, second]


def test_process_next_processes_transactions_in_fifo_order():
    manager = create_pending_manager()
    first = manager.enqueue_transaction(IncomeTransaction("tx-1", 50, "cash", "salary"))
    second = manager.enqueue_transaction(ExpenseTransaction("tx-2", 20, "cash", "food"))

    assert manager.process_next() is first
    assert manager.process_next() is second
    assert manager.transaction_manager.get_transaction("tx-1") is first
    assert manager.transaction_manager.get_transaction("tx-2") is second
    assert manager.transaction_manager.account_manager.get_account("cash").balance == 130
    assert manager.list_pending() == []


def test_process_next_moves_transaction_to_transaction_manager():
    manager = create_pending_manager()
    transaction = manager.enqueue_transaction(IncomeTransaction("tx-1", 50, "cash", "salary"))

    processed = manager.process_next()

    assert processed is transaction
    assert manager.transaction_manager.get_transaction("tx-1") is transaction
    assert manager.transaction_manager.account_manager.get_account("cash").balance == 150
    assert manager.peek_next() is None


def test_empty_queue_peek_next_returns_none():
    manager = create_pending_manager()

    assert manager.peek_next() is None


def test_empty_queue_process_next_returns_none():
    manager = create_pending_manager()

    assert manager.process_next() is None


def test_enqueue_rejects_duplicate_id_in_pending_queue():
    manager = create_pending_manager()
    manager.enqueue_transaction(IncomeTransaction("tx-1", 50, "cash", "salary"))

    with pytest.raises(DuplicateRecordError):
        manager.enqueue_transaction(ExpenseTransaction("tx-1", 20, "cash", "food"))


def test_enqueue_rejects_duplicate_id_already_processed():
    manager = create_pending_manager()
    manager.transaction_manager.add_transaction(IncomeTransaction("tx-1", 50, "cash", "salary"))

    with pytest.raises(DuplicateRecordError):
        manager.enqueue_transaction(ExpenseTransaction("tx-1", 20, "cash", "food"))


def test_process_failure_keeps_transaction_at_queue_head_and_balance_unchanged():
    manager = create_pending_manager()
    transaction = manager.enqueue_transaction(ExpenseTransaction("tx-1", 150, "cash", "food"))

    with pytest.raises(InsufficientFundsError):
        manager.process_next()

    assert manager.peek_next() is transaction
    assert manager.list_pending() == [transaction]
    assert manager.transaction_manager.account_manager.get_account("cash").balance == 100
