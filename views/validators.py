from business_logic.constants import BusinessConstants
from datetime import date, timedelta
from wtforms.validators import (ValidationError)

class Age(object):
    """Checks if date entered is in proper range for age restirctions"""
    def __init__(self, min=BusinessConstants.MINIMUM_AGE, max=BusinessConstants.MAXIMUM_AGE, message=None):
        self.min = min
        self.max = max
        if not message:
            message=f"Age must be between {min} and {max} years"
        self.message = message

    def __call__(self, form, field):
        age = (date.today() - field.data).days / 365
        if not self.min < age < self.max:
            raise ValidationError(self.message)
        
class CheckIfFormHasData(object):
    """Checks if field has any data in it"""
    def __init__(self, message=None):
        if not message:
            message = "No fields filled in"
        self.message = message

    def __call__(self, form, field):
        for field in form:
            if not field.data:
                break
        else:
            raise ValidationError(self.message)

class CheckIfAllPasswordFieldsHaveDataIfOneHasData(object):
    """Checks if password fields have been filled in"""
    def __init__(self, message=None):
        if not message:
            message = "Missing required password field"
        self.message = message

    def __call__(self, form, field):
        password_fields = [field for field_name, field in form._fields.items() if "password" in field_name]
        filled_password_fields = [True if field.data else False for field in password_fields]
        
        if any(filled_password_fields) and not all(filled_password_fields):
            raise ValidationError(self.message)