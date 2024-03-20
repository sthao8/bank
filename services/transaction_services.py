from decimal import Decimal
from datetime import datetime, timedelta, date
from repositories.transaction_repository import TransactionRepository
from models import Account, Customer, Transaction
from services.account_services import AccountService
from constants.constants import TransactionTypes
from constants.errors_messages import ErrorMessages

class TransactionService():
    def __init__(self,
                 transaction_repository: TransactionRepository,
                 account_service: AccountService
                 ) -> None:
        self.transaction_repository = transaction_repository
        self.account_service = account_service

    def _calculate_new_balance(self,
                               account: Account,
                               amount: Decimal,
                               transaction_type: TransactionTypes
                               ) -> Decimal:
        """Calculates new balance depending on transaction type"""
        if transaction_type == TransactionTypes.DEPOSIT:
            return account.balance + amount
        elif transaction_type == TransactionTypes.WITHDRAW:
            return account.balance - amount

    def initiate_transaction_process(self,
                                     account_id: int,
                                     amount: Decimal,
                                     transaction_type_name: str,
                                     to_account_id: int=None
                                     ) -> list[Transaction]:
        """Determines where to send transaction depending on transaction type,
        must provide to_account if type is transfer"""
        from_account = self.account_service.get_account_from_id(account_id, raise_404=False)
        if not from_account:
            raise ValueError(ErrorMessages.UNKNOWN_ACCOUNT.value)

        if transaction_type_name == "transfer":
            if not to_account_id:
                raise ValueError("To account not specified for a transfer!")

            to_account = self.account_service.get_account_from_id(to_account_id, raise_404=False)
            if not to_account:
                raise ValueError(ErrorMessages.UNKNOWN_ACCOUNT.value)
            
            return self.process_transfer(from_account, to_account, amount)
        else:
            transaction_type = TransactionTypes.get_type_by_value(transaction_type_name)
            return [self.process_transaction(from_account, amount, transaction_type)]

    def process_transaction(self,
                            target_account: Account,
                            amount: Decimal,
                            transaction_type: TransactionTypes
                            ) -> Transaction:
        """Checks amount for negatives/zero and against account balance, finally executing transaction"""
        if amount < 0:
            raise ValueError(ErrorMessages.NEGATIVE_AMOUNT.value)
        
        if transaction_type == TransactionTypes.WITHDRAW:
            if amount > target_account.balance:
                raise ValueError(ErrorMessages.INSUFFICIENT_FUNDS.value)
            
        new_balance = self._calculate_new_balance(target_account, amount, transaction_type)      
        return self.transaction_repository.execute_transaction(
            target_account,
            amount,
            transaction_type,
            new_balance)

    def process_transfer(self,
                         from_account: Account,
                         to_account: Account,
                         amount: Decimal
                         ) -> list[Transaction]:
        """Initiates two transactions, withdraw from from_account and deposit into to_account"""
        withdraw_transaction = self.process_transaction(from_account, amount, TransactionTypes.WITHDRAW)
        deposit_transaction = self.process_transaction(to_account, amount, TransactionTypes.DEPOSIT)
        return [withdraw_transaction, deposit_transaction]

    def get_count_of_transactions(self, account_id: int) -> int:
        return self.transaction_repository.get_count_of_transactions(account_id)
    
    def get_limited_offset_transactions(self,
                                        account_id: int,
                                        limit: int,
                                        offset: int
                                        ) -> list[Transaction]:
        return self.transaction_repository.get_limited_offset_transactions(account_id, limit, offset)
    
    def get_sum_transactions_of_customer(self,
                                       customer: Customer,
                                       time_period: timedelta
                                       ) -> Decimal:
        from_date = datetime.now() - time_period
        sum = self.transaction_repository.get_sum_transactions_of_customer(customer, from_date)
        return Decimal(sum) if sum is not None else 0
    
    def get_summed_transactions(self,
                                customer: Customer,
                                time_period: timedelta
                                ) -> list[Transaction]:
        from_date = datetime.now() - time_period
        return self.transaction_repository.get_summed_transactions(customer, from_date)
    
    def get_transactions_for_customer_on_date(self,
                                              customer: Customer,
                                              target_date: date
                                              ) -> list[Transaction]:
        return self.transaction_repository.get_transactions_for_customer_on_date(customer, target_date)