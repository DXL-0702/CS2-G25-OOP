from .doubly_linked_list import DoublyLinkedList

class Stack:
    """
    A LIFO (Last-In-First-Out) stack for undo operations.
    Stores operations to support rollback of financial actions.
    """
    def __init__(self):
        self.dll = DoublyLinkedList()

    def push(self, data):
        self.dll.append(data)

    def pop(self):
        return self.dll.pop_tail()

    def peek(self):
        return self.dll.peek_tail()

    def is_empty(self):
        return self.dll.is_empty()

    def size(self):
        return self.dll.size
