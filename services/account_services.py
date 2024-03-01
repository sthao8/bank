from repositories.account_repository import AccountRepository

class AccountService():
    def __init__(self, account_repository: AccountRepository) -> None:
        self.account_repository = account_repository

    def get_account_from_id(self, account_id: int, raise_404: bool=False):
        return self.account_repository.get_account_from_id(account_id, raise_404)
    
    def get_account_choices(self, customer):
        return self.account_repository.get_account_choices(customer)