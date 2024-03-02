from repositories.account_repository import AccountRepository
from constants.constants import AccountTypes
from datetime import datetime
from utils import format_money

class AccountService():
    def __init__(self, account_repository: AccountRepository) -> None:
        self.account_repository = account_repository

    def get_account_from_id(self, account_id: int, raise_404: bool=False):
        return self.account_repository.get_account_from_id(account_id, raise_404)
    
    def get_account_choices(self, customer):
        return [
            (account.id, f"{account.id}: current balance: {format_money(account.balance)}")
            for account in customer.accounts
            ]
    
    def create_account_for_new_customer(self, customer_id: int):
        """Creates a new empty checking account for new customer"""
        account_information = {
            "account_type": AccountTypes.CHECKING.value,
            "created": datetime.now(),
            "balance": 0,
            "customer_id": customer_id
        }
        return self.account_repository.create_account_for_customer(account_information)