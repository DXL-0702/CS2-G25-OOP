class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, child_data):
        child = TreeNode(child_data)
        self.children.append(child)
        return child


class Tree:
    """
    A general-purpose tree structure for category hierarchy.
    Supports recursive traversal to organize financial categories.
    """
    def __init__(self, root_data):
        self.root = TreeNode(root_data)

    @staticmethod
    def add_child(parent_node, child_data):
        return parent_node.add_child(child_data)

    @staticmethod
    def preorder(node):
        if node is None:
            return []
        result = [node.data]
        for child in node.children:
            result.extend(Tree.preorder(child))
        return result

    @staticmethod
    def find(node, target):
        if node is None:
            return None
        if node.data == target:
            return node
        for child in node.children:
            found = Tree.find(child, target)
            if found is not None:
                return found
        return None

    @staticmethod
    def level_order(node):
        if node is None:
            return []
        result = []
        queue = [node]
        while queue:
            current = queue.pop(0)
            result.append(current.data)
            queue.extend(current.children)
        return result

    @staticmethod
    def format_path(items):
        return " -> ".join(str(item) for item in items)
