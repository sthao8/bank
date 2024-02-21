from repositories.customer_repository import CustomerRepository

class CustomerService():
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    def get_customer_or_none(self, customer_id):
        return self.customer_repository.get_customer_or_none(customer_id)
    
    def get_customer_or_404(self, customer_id):
        return self.customer_repository.get_customer_joined_accounts_country_or_404(customer_id)
    
    def get_all_customers_for(self, country):
        return self.customer_repository.get_all_customers_for(country)
    
    def get_customer_from_transaction(self, transaction):
        return self.customer_repository.get_customer_from_transaction(transaction)

    def create_customer_and_new_account(self, form):
        national_id = form.register_national_id.data
        customer = self.customer_repository.get_customer_from_national_id(national_id)

        if customer:
            raise ValueError(f"Account with national id {national_id} already exists")
        else:
            return self.customer_repository.create_customer_and_new_account(form)