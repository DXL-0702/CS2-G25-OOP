from datetime import datetime

class BaseRecord:
    def __init__(self, id: str = None):
        self.id = id
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def touch(self):
        """更新 updated_at 为当前时间"""
        self.updated_at = datetime.now()

    def to_dict(self):
        """返回包含所有字段的字典"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }