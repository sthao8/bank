from enum import Enum

class ErrorMessages(Enum):
    INSUFFICIENT_FUNDS = "Insufficient funds for transaction"
    NEGATIVE_AMOUNT = "Amount cannot be negative or 0"
    UNKNOWN_ACCOUNT = "Cannot find account"
    NATIONAL_ID_NOT_UNIQUE = "National ID is already associated with a customer "
    EMAIL_NOT_UNIQUE = "Email is already associated with a user"
    NEW_PW_IS_OLD = "New password cannot be the same as old password"
    INVALID_LOGIN = "Invalid email or password"
    PW_DO_NOT_MATCH = "Passwords do not match"
    PW_WRONG_LENGTH = "Password must be between 8 and 32 characters"
    SAME_ACCOUNT = "You have entered the same account number for transfers"
    ACCOUNT_ID_INT = "Only numbers allowed for account ID"