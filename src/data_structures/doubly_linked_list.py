class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """
    A doubly linked list used to maintain transaction history timeline.
     Supports efficient insertion, deletion, and traversal in both directions.
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def prepend(self, data):
        new_node = Node(data)
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def remove(self, data):
        current = self.head
        while current:
            if current.data == data:
                self._unlink(current)
                return data
            current = current.next
        return None

    def pop_head(self):
        if self.is_empty():
            return None
        data = self.head.data
        self._unlink(self.head)
        return data

    def pop_tail(self):
        if self.is_empty():
            return None
        data = self.tail.data
        self._unlink(self.tail)
        return data

    def peek_head(self):
        return None if self.is_empty() else self.head.data

    def peek_tail(self):
        return None if self.is_empty() else self.tail.data

    def is_empty(self):
        return self.size == 0

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def to_reversed_list(self):
        result = []
        current = self.tail
        while current:
            result.append(current.data)
            current = current.prev
        return result

    def traverse_forward(self):
        return " <-> ".join(str(item) for item in self.to_list())

    def traverse_backward(self):
        return " <-> ".join(str(item) for item in self.to_reversed_list())

    def _unlink(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None
        self.size -= 1
