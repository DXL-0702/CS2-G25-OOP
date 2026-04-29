class FinanceError(Exception):
    pass


class ValidationError(FinanceError):
    pass


class InvalidAmountError(ValidationError):
    pass


class InvalidDateError(ValidationError):
    pass


class InsufficientFundsError(FinanceError):
    pass


class RecordNotFoundError(FinanceError):
    pass


class DuplicateRecordError(FinanceError):
    pass


class DataStorageError(FinanceError):
    pass


__all__ = [
    "DataStorageError",
    "DuplicateRecordError",
    "FinanceError",
    "InsufficientFundsError",
    "InvalidAmountError",
    "InvalidDateError",
    "RecordNotFoundError",
    "ValidationError",
]
