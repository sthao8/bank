from repositories.customer_repository import CustomerRepository
from services.account_services import AccountService
from models import Customer, Country
from constants.errors_messages import ErrorMessages

class CustomerService():
    def __init__(self,
                 customer_repository: CustomerRepository,
                 account_service: AccountService
                 ) -> None:
        self.customer_repository = customer_repository
        self.account_service = account_service

    def get_customer_from_id(self, customer_id: int, raise_404: bool=False) -> Customer|None:
        return self.customer_repository.get_customer_from_id(customer_id, raise_404)
    
    def get_customer_accounts_country(self, customer_id: int) -> Customer:
        return self.customer_repository.get_customer_joined_accounts_country_or_404(customer_id)
    
    def get_all_customers_for_country(self, country: Country) -> list[Customer]:
        return self.customer_repository.get_all_customers_for_country(country)
    
    def get_top_10_customers_for_country(self, country_name: str) -> list[Customer]:
        return self.customer_repository.get_top_10_customers_for_country(country_name)
    
    def get_customer_from_national_id(self, national_id: str) -> Customer|None:
        return self.customer_repository.get_customer_from_national_id(national_id)
    
    def customer_edited(self, customer: Customer, customer_details: dict) -> bool:
        """Compares new customer_details to customer. If changes exist, edits the model."""
        for attribute_name, value in customer_details.items():
            if getattr(customer, attribute_name) != value: # if there is a difference
                self.customer_repository.edit_customer(customer, customer_details)
                return True
        return False

    def create_customer_and_new_account(self, customer_details: dict) -> Customer:
        """Checks that national ID is unique before creating customer and account"""
        national_id = customer_details["national_id"]
        customer = self.customer_repository.get_customer_from_national_id(national_id)

        if customer:
            raise ValueError(ErrorMessages.NATIONAL_ID_NOT_UNIQUE.value)
        else:
            new_customer = self.customer_repository.create_customer(customer_details)
            print(new_customer.id)
            self.account_service.create_account_for_new_customer(new_customer.id)

        return new_customer