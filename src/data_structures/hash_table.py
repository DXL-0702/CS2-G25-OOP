class HashTable:
    """
    A hash table for fast ID-based lookup of financial records.
    Provides average O(1) time complexity for insert, get, and delete operations.
    """
    def __init__(self, size=10):
        if size <= 0:
            raise ValueError("Hash table size must be positive")
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                pair[1] = value
                return
        self.table[index].append([key, value])

    def get(self, key):
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                return pair[1]
        return None

    def remove(self, key):
        index = self._hash(key)
        for i, pair in enumerate(self.table[index]):
            if pair[0] == key:
                del self.table[index][i]
                return pair[1]
        return None

    def contains(self, key):
        index = self._hash(key)
        return any(pair[0] == key for pair in self.table[index])
