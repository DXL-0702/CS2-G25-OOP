from .doubly_linked_list import DoublyLinkedList


class Queue:
    """
    A FIFO (First-In-First-Out) queue for pending transactions.
    Processes transactions in the order they are received.
    """
    def __init__(self):
        self.dll = DoublyLinkedList()

    def enqueue(self, data):
        self.dll.append(data)

    def dequeue(self):
        return self.dll.pop_head()

    def peek(self):
        return self.dll.peek_head()

    def is_empty(self):
        return self.dll.is_empty()

    def size(self):
        return self.dll.size
