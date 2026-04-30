class Budget:
    """Represents a budget for a specific category and period."""

    def __init__(self, budget_id: str, category_id: str, period: str,
                 limit_amount: float, spent_amount: float = 0.0):
        self.budget_id = budget_id
        self.category_id = category_id
        self.period = period
        self.limit_amount = limit_amount
        self.spent_amount = spent_amount

    def remaining_amount(self) -> float:
        """Calculate the remaining budget amount."""
        return self.limit_amount - self.spent_amount

    def is_over_budget(self) -> bool:
        """Return True if spent_amount strictly exceeds limit_amount."""
        return self.spent_amount > self.limit_amount

    def to_dict(self):
        return {
            "budget_id": self.budget_id,
            "category_id": self.category_id,
            "period": self.period,
            "limit_amount": self.limit_amount,
            "spent_amount": self.spent_amount,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            budget_id=data["budget_id"],
            category_id=data["category_id"],
            period=data["period"],
            limit_amount=data["limit_amount"],
            spent_amount=data.get("spent_amount", 0.0),
        )
