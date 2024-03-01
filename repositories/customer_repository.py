from datetime import datetime
from constants.constants import AccountTypes
from models import Customer, Account, db, Country, Transaction
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from views.forms import FlaskForm

class CustomerRepository():
    def get_customer_or_none(self, customer_id):
        return Customer.query.filter_by(id=customer_id).one_or_none() 

    def get_customer_joined_accounts_country_or_404(self, customer_id):
        return Customer.query.filter_by(id=customer_id).options(
            joinedload(Customer.accounts),
            joinedload(Customer.country_details)
            ).one_or_404()
    
    def get_customer_from_national_id(self, national_id):
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
    
    def get_customer_from_national_id_or_404(self, national_id):
        return Customer.query.filter_by(national_id=national_id).one_or_404()
    
    def edit_customer(self, customer, customer_details: dict):
        for attribute_name, value in customer_details.items():
            setattr(customer, attribute_name, value)
    
    def create_customer_and_new_account(self, form: FlaskForm) -> Customer:
        new_customer = Customer()

        for field_name, field in form._fields.items():
            if field_name in form.user_defined_fields:
                setattr(new_customer, field_name, field.data)

        new_account = Account()
        new_account.account_type = AccountTypes.CHECKING.value
        new_account.created = datetime.now()
        new_account.balance = 0 # TODO: not sure about this. maybe all accounts should start with 0?
        new_customer.accounts.append(new_account)

        db.session.add(new_customer)
        db.session.commit()

        return new_customer