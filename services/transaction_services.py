from decimal import Decimal
from repositories.transaction_repository import TransactionRepository
from business_logic.constants import TransactionTypes

class TransactionService():
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository

    def process_transaction(self, target_account, amount, transaction_type: TransactionTypes):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        if transaction_type == TransactionTypes.WITHDRAW:
            if amount > target_account.balance:
                raise ValueError("Insufficient funds for withdrawal.")
            else:
                amount = -amount
        
        self.transaction_repository.execute_transaction(target_account, amount, transaction_type)

    def process_transfer(self, from_account, to_account, amount):
        self.process_transaction(from_account, amount, TransactionTypes.WITHDRAW)
        self.process_transaction(to_account, amount, TransactionTypes.DEPOSIT)

    def get_count_of_transactions(self, account_id):
        return self.transaction_repository.get_count_of_transactions(account_id)
    
    def get_limited_offset_transactions(self, account_id, limit, offset):
        return self.transaction_repository.get_limited_offset_transactions(account_id, limit, offset)
    
    def get_sum_recent_transactions_of(self, customer, time_period):
        sum = self.transaction_repository.get_sum_recent_transactions_of_country(customer, time_period)
        return Decimal(sum) if sum is not None else 0
    
    def get_summed_transaction_ids(self, customer, time_period):
        return self.transaction_repository.get_summed_transaction_ids(customer, time_period)
    
    def get_recent_unchecked_transactions_for(self, customer, from_datetime):
        return self.transaction_repository.get_recent_unchecked_transactions_for(customer, from_datetime)