from src.data_structures.queue import Queue
from src.exceptions import DuplicateRecordError


class PendingTransactionManager:
    def __init__(self, transaction_manager):
        self.transaction_manager = transaction_manager
        self.pending_queue = Queue()

    def enqueue_transaction(self, transaction):
        if self.transaction_manager.transactions.contains(transaction.transaction_id):
            raise DuplicateRecordError(
                f"Transaction already exists: {transaction.transaction_id}"
            )
        if any(
            pending.transaction_id == transaction.transaction_id
            for pending in self.list_pending()
        ):
            raise DuplicateRecordError(
                f"Pending transaction already exists: {transaction.transaction_id}"
            )

        self.pending_queue.enqueue(transaction)
        return transaction

    def process_next(self):
        transaction = self.peek_next()
        if transaction is None:
            return None

        processed = self.transaction_manager.add_transaction(transaction)
        self.pending_queue.dequeue()
        return processed

    def peek_next(self):
        return self.pending_queue.peek()

    def list_pending(self):
        return self.pending_queue.dll.to_list()
