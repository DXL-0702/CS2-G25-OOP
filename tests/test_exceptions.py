import pytest

from src.exceptions import (
    DataStorageError,
    DuplicateRecordError,
    FinanceError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidDateError,
    RecordNotFoundError,
    ValidationError,
)


ALL_CUSTOM_EXCEPTIONS = [
    ValidationError,
    InvalidAmountError,
    InvalidDateError,
    InsufficientFundsError,
    RecordNotFoundError,
    DuplicateRecordError,
    DataStorageError,
]


def test_all_custom_exceptions_inherit_finance_error():
    for exception_type in ALL_CUSTOM_EXCEPTIONS:
        assert issubclass(exception_type, FinanceError)


def test_validation_errors_share_validation_base_class():
    assert issubclass(InvalidAmountError, ValidationError)
    assert issubclass(InvalidDateError, ValidationError)


def test_custom_exception_message_is_preserved():
    with pytest.raises(InvalidAmountError) as error_info:
        raise InvalidAmountError("amount must be positive")

    assert str(error_info.value) == "amount must be positive"


def test_finance_error_can_catch_domain_errors():
    with pytest.raises(FinanceError):
        raise RecordNotFoundError("record was not found")
