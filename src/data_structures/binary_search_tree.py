class BSTNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = key if value is None else value
        self.left = None
        self.right = None

    @property
    def data(self):
        return self.key


class BinarySearchTree:
    """
    A binary search tree optimized for amount range queries.
    Maintains sorted order to support efficient range-based lookups.
    """
    def __init__(self):
        self.root = None

    def insert(self, key, value=None):
        new_node = BSTNode(key, value)
        if self.root is None:
            self.root = new_node
            return
        self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current, new_node):
        if new_node.key < current.key:
            if current.left is None:
                current.left = new_node
            else:
                self._insert_recursive(current.left, new_node)
        else:
            if current.right is None:
                current.right = new_node
            else:
                self._insert_recursive(current.right, new_node)

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        if node is None:
            return None
        if key == node.key:
            return node.value
        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)

    def inorder_list(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node is None:
            return
        self._inorder_recursive(node.left, result)
        result.append(node.value)
        self._inorder_recursive(node.right, result)

    def range_query(self, minimum, maximum):
        result = []
        self._range_query_recursive(self.root, minimum, maximum, result)
        return result

    def _range_query_recursive(self, node, minimum, maximum, result):
        if node is None:
            return
        if node.key > minimum:
            self._range_query_recursive(node.left, minimum, maximum, result)
        if minimum <= node.key <= maximum:
            result.append(node.value)
        if node.key < maximum:
            self._range_query_recursive(node.right, minimum, maximum, result)

    def inorder(self, node=None, res=None):
        values = self.inorder_list() if node is None and res is None else self._legacy_inorder(node, res)
        return " -> ".join(str(item) for item in values)

    def _legacy_inorder(self, node, res=None):
        if res is None:
            res = []
        if node is not None:
            self._legacy_inorder(node.left, res)
            res.append(node.value)
            self._legacy_inorder(node.right, res)
        return res
