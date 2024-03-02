from enum import Enum

class ErrorMessages(Enum):
    INSUFFICIENT_FUNDS = "Insufficient funds for transaction"
    NEGATIVE_AMOUNT = "Amount cannot be negative"
    UNKNOWN_ACCOUNT = "Cannot find account"
    NATIONAL_ID_NOT_UNIQUE = "National ID is already associated with a customer "
    EMAIL_NOT_UNIQUE = "Email is already associated with a user"
    NEW_PW_IS_OLD = "New password cannot be the same as old password"
    INVALID_LOGIN = "Invalid username or password"