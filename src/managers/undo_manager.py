from src.data_structures.stack import Stack
from src.exceptions import ValidationError


class UndoManager:
    def __init__(self, transaction_manager):
        self.transaction_manager = transaction_manager
        self.history = Stack()

    def record_add_transaction(self, transaction):
        operation = {
            "action": "add_transaction",
            "transaction_id": transaction.transaction_id,
        }
        self.history.push(operation)
        return operation

    def undo_last(self):
        operation = self.history.pop()
        if operation is None:
            return None

        if operation["action"] == "add_transaction":
            return self.transaction_manager.delete_transaction(operation["transaction_id"])

        raise ValidationError(f"Unsupported undo action: {operation['action']}")

    def has_history(self):
        return not self.history.is_empty()

    def history_size(self):
        return self.history.size()
