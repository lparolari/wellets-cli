import uuid
from typing import Any, Callable, List, Union

Validator = Callable[[str], Union[str, bool]]


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


def and_validator(validators: List[Validator]):
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


def each_validator(validator: Validator):
    def wrapper(vals: List[str]):
        for val in vals:
            outcome = validator(val)
            if outcome != True:
                return outcome
        return True

    return wrapper


def validate(validator: Validator, value: Any):
    if value is not None:
        outcome = validator(value)
        if outcome != True:
            raise ValueError(outcome)
