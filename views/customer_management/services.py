from business_logic.constants import AccountTypes
from datetime import datetime
from models import Customer, Account, Transaction, Country, db
from sqlalchemy.orm import joinedload

def get_customer_from_id(customer_id):
    return Customer.query.filter_by(id=customer_id).options(
        joinedload(Customer.accounts),
        joinedload(Customer.country_details)
        ).one_or_404()

def get_account_from_id(account_id):
    return Account.query.filter_by(id=account_id).one_or_404()

def get_transactions_from_account_id(account_id):
    return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).all()

def get_all_countries():
    return Country.query.all()

def create_customer(form) -> Customer:
    new_customer = Customer()

    for field_name, field in form._fields.items():
        if field_name.startswith(form.field_prefix):
            model_col_name = form.get_column_name(field_name)
            setattr(new_customer, model_col_name, field.data)

    new_account = Account()
    new_account.account_type = AccountTypes.CHECKING.value
    new_account.created = datetime.now()
    new_account.balance = 0 # TODO: not sure about this. maybe all accounts should start with 0?
    new_customer.accounts.append(new_account)

    return new_customer
