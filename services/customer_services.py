from repositories.customer_repository import CustomerRepository
from models import Customer

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
    
    def get_customer_from_national_id(self, national_id):
        return self.customer_repository.get_customer_from_national_id_or_404(national_id)
    
    def customer_edited(self, customer: Customer, customer_details: dict) -> bool:
        """Compares new customer_details to customer. If changes, edits the model."""
        for attribute_name, value in customer_details.items():
            if getattr(customer, attribute_name) != value: # if there is a difference
                self.customer_repository.edit_customer(customer, customer_details)
                return True
        return False


    def create_customer_and_new_account(self, form):
        national_id = form.national_id.data
        customer = self.customer_repository.get_customer_from_national_id(national_id)

        if customer:
            raise ValueError(f"Account with national id {national_id} already exists")
        else:
            return self.customer_repository.create_customer_and_new_account(form)