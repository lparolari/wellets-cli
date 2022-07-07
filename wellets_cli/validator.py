import uuid
from datetime import datetime
from typing import Any, Callable, List, Union

from InquirerPy.validator import ValidationError, Validator

Validator2 = Callable[[str], Union[str, bool]]

# TODO: replace this validators in favor of `Validator` subclasses
def validate(validator: Validator2, value: Any):
    if value is not None:
        outcome = validator(value)
        if outcome != True:
            raise ValueError(outcome)


def percent_validator(val: str):
    return (
        True
        if float(val) >= 0 and float(val) <= 100
        else "Should be a percentage"
    )


def not_empty_validator(val: str):
    return True if val != "" else "Should not be empty"


def number_validator(val: str):
    try:
        float(val)
        return True
    except ValueError:
        return "Should be a number"


def and_validator(validators: List[Validator2]):
    def wrapper(val: str):
        for validator in validators:
            validated = validator(val)
            if not validated == True:
                return validated
        return True

    return wrapper


def uuid_validator(val: str):
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return "Should be a UUID"


def each_validator(validator: Validator2):
    def wrapper(vals: List[str]):
        for val in vals:
            outcome = validator(val)
            if outcome != True:
                return outcome
        return True

    return wrapper


class GreaterThanValidator(Validator):
    def __init__(
        self,
        lower_bound: int = 0,
        message: str = "Input must be greater than {}",
    ) -> None:
        self._lower_bound = lower_bound
        self._message = message

    def validate(self, document):
        if float(document.text) <= self._lower_bound:
            raise ValidationError(
                message=self._message.format(self._lower_bound),
                cursor_position=document.cursor_position,
            )


class GreaterThanOrEqualValidator(Validator):
    def __init__(
        self,
        lower_bound: int = 0,
        message: str = "Input must be greater or equal than {}",
        allow_equal: bool = False,
    ) -> None:
        self._lower_bound = lower_bound
        self._message = message

    def validate(self, document):
        if float(document.text) < self._lower_bound:
            raise ValidationError(
                message=self._message.format(self._lower_bound),
                cursor_position=document.cursor_position,
            )


class AndValidator(Validator):
    def __init__(self, validators: List[Validator]):
        self._validators = validators

    def validate(self, document):
        for validator in self._validators:
            validator.validate(document)


class DateValidator(Validator):
    def __init__(
        self,
        message: str = "Input should be a date",
        date_fmt: str = "%Y-%m-%d %H:%M",
    ) -> None:
        self._message = message
        self._date_fmt = date_fmt

    def validate(self, document):
        if document.text != "":
            try:
                datetime.strptime(document.text, self._date_fmt)
            except ValueError:
                raise ValidationError(
                    message=self._message,
                    cursor_position=document.cursor_position,
                )
