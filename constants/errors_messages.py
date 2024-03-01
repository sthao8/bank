from enum import Enum

class ErrorMessages(Enum):
    INSUFFICIENT_FUNDS = "Insufficient funds for transaction"
    NEGATIVE_AMOUNT = "Amount cannot be negative"
    UNKNOWN_ACCOUNT = "Cannot find account"
    NATIONAL_ID_EXISTS = "Provided national ID not unique"
