from models import Customer, Account, db, Country, Transaction
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class CustomerRepository():
    def get_customer_or_none(self, customer_id):
        return Customer.query.filter_by(id=customer_id).one_or_none() 

    def get_customer_joined_accounts_country_or_404(self, customer_id):
        return Customer.query.filter_by(id=customer_id).options(
            joinedload(Customer.accounts),
            joinedload(Customer.country_details)
            ).one_or_404()
    
    def get_customer_from_national_id(self, national_id: str) -> Customer:
        return Customer.query.filter_by(national_id=national_id).one_or_none()
    
    def get_all_customers_for(self, country: Country):
        return Customer.query.filter_by(country=country.country_code).all()

    def get_customer_from_transaction(self, transaction: Transaction):
        return db.session.execute(
            select(Customer)
            .join(Account, Account.customer_id==Customer.id)
            .join(Transaction, Transaction.account_id==Account.id)
            .where(Transaction.id==transaction.id)
        ).scalar_one_or_none()

    def edit_customer(self, customer, customer_details: dict):
        for attribute_name, value in customer_details.items():
            setattr(customer, attribute_name, value)
        db.session.commit()

    def create_customer(self, customer_details: dict) -> Customer:
        new_customer = Customer()

        for attribute_name, value in customer_details.items():
            setattr(new_customer, attribute_name, value)
        
        db.session.add(new_customer)
        db.session.commit()

        return new_customer