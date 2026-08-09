import re

from django.core.exceptions import ValidationError

from datetime import date


def validate_name(value):

    if not value.strip():
        raise ValidationError(
            "This field cannot be empty."
        )

    if not value.replace(" ", "").isalpha():
        raise ValidationError(
            "Only alphabetic characters are allowed."
        )


def validate_phone(value):

    if not re.fullmatch(r"\d{10}", value):
        raise ValidationError(
            "Phone number must contain exactly 10 digits."
        )


def validate_date_of_birth(value):

    if value > date.today():
        raise ValidationError(
            "Date of birth cannot be in the future."
        )