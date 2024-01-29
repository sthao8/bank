from datetime import date
from enum import Enum


class TelephoneCountryCodes(Enum):
    fi_FI = "+358"  # Finland
    no_NO = "+47"   # Norway
    sv_SE = "+46"   # Sweden

class TransactionTypes(Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"

class TransactionOperations(Enum):
    DEBIT_OPERATIONS = ("Deposit cash", "Salary", "Transfer")
    CREDIT_OPERATIONS = ("ATM withdrawal", "Payment", "Bank withdrawal", "Transfer")

class BusinessConstants:
    SUPPORTED_LOCALES = [supported_country_locale.name for supported_country_locale in TelephoneCountryCodes]
    MINIMUM_AGE = 18
    MAXIMUM_AGE = 100
    BANK_ESTABLISHED_DATE = date(year=1905, month=12, day=5)

class AccountTypes(Enum):
    PERSONAL = "Personal"
    CHECKING = "Checking"
    SAVINGS = "Savings"
