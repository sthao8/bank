from repositories.account_repository import AccountRepository

class AccountService():
    def __init__(self, account_repository: AccountRepository) -> None:
        self.account_repository = account_repository

    def get_account_or_404(self, account_id):
        return self.account_repository.get_account_or_404(account_id)
    
    def get_account_choices(self, customer):
        return self.account_repository.get_account_choices(customer)