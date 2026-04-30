class CategoryNode:
    """Represents a node in the category tree."""

    def __init__(self, category_id: str, name: str, parent_id: str = None):
        self.category_id = category_id
        self.name = name
        self.parent_id = parent_id
        self.children = []

    def add_child(self, child_node):
        """Add a child category and update its parent_id."""
        child_node.parent_id = self.category_id
        self.children.append(child_node)

    def to_dict(self):
        """Recursively convert the node and its children to a dictionary."""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data):
        category = cls(
            category_id=data["category_id"],
            name=data["name"],
            parent_id=data.get("parent_id"),
        )
        for child_data in data.get("children", []):
            category.add_child(cls.from_dict(child_data))
        return category
