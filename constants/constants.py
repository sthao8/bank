from datetime import date
from enum import Enum


class TelephoneCountryCodes(Enum):
    """Add a country code (as supported by Faker) and country phone code here
    to be able to seed data for that country"""
    fi_FI = "+358"  # Finland
    no_NO = "+47"   # Norway
    sv_SE = "+46"   # Sweden
    de_DE = "+49"   # Germany

class TransactionTypes(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

    @classmethod
    def get_type_by_value(cls, value):
        """Returns the enum type given the value"""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid value in {cls.__name__}")

class BusinessConstants:
    SUPPORTED_LOCALES = [supported_country_locale.name for supported_country_locale in TelephoneCountryCodes]
    MINIMUM_AGE = 18
    MAXIMUM_AGE = 100
    BANK_ESTABLISHED_DATE = date(year=1905, month=12, day=5)

class AccountTypes(Enum):
    PERSONAL = "Personal"
    CHECKING = "Checking"
    SAVINGS = "Savings"

class UserRoles(Enum):
    ADMIN = "admin"
    CASHIER = "cashier"