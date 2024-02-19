from repositories.transaction_repository import TransactionRepository
from business_logic.constants import TransactionTypes

class TransactionService():
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository

    def process_transaction(self, target_account, amount, transaction_type: TransactionTypes):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        if transaction_type == TransactionTypes.WITHDRAW and amount > target_account.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        
        self.transaction_repository.create_transaction(target_account, amount, transaction_type)

    def process_transfer(self, from_account, to_account, amount):
        self.process_transaction(from_account, amount, TransactionTypes.WITHDRAW)
        self.process_transaction(to_account, amount, TransactionTypes.DEPOSIT)
