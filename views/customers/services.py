from business_logic.constants import AccountTypes
from datetime import datetime
from models import Customer, Account, Transaction, Country, db
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, desc, asc


def get_country_or_404(country_name):
    return Country.query.filter(func.lower(Country.name)==country_name.lower()).one_or_404()

def get_country_customer(country):
    return db.session.execute(
            select(
            Customer, 
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Account, Account.customer_id==Customer.id)
            .join(Country, Country.country_code==Customer.country)
            .where(Country.name==country)
            .group_by(Customer.id)
            .order_by(desc("sum_of_accounts"))
            .limit(10)
            ).all()

def get_customer_or_404(customer_id):
    return Customer.query.filter_by(id=customer_id).options(
        joinedload(Customer.accounts),
        joinedload(Customer.country_details)
        ).one_or_404()

def get_account_or_404(account_id):
    return Account.query.filter_by(id=account_id).one_or_404()

def get_limited_offset_transactions(account_id, transactions_per_page, page):
    offset_value = (page - 1) * transactions_per_page
    return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).limit(transactions_per_page).offset(offset_value).all()

def get_count_of_transactions(account_id):
    return Transaction.query.filter_by(account_id=account_id).count()

def get_all_countries():
    return Country.query.all()

def create_customer_and_new_account(form) -> Customer:
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

def get_country_stats():
    return db.session.execute(
        select(
            Country.name,
            func.count(func.distinct(Customer.id)).label("number_of_customers"),
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Customer, Customer.country==Country.country_code)
            .join(Account, Account.customer_id==Customer.id)
            .group_by(Customer.country)
            .order_by(desc("sum_of_accounts"))
            ).all()

class TransactionsApiModel:
    def __init__(self, transaction: Transaction) -> None:
        self.id = transaction.id
        self.type = transaction.type
        self.timestamp = transaction.timestamp
        self.amount = transaction.amount
        self.new_balance = transaction.new_balance
        self.account_id = transaction.account_id

    def to_dict(self):
        """ Converts api model instance into a dictionary """
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "new_balance": self.new_balance,
            "account_id": self.account_id
        }

class CustomerApiModel:
    def __init__(self, customer: Customer) -> None:
        self.id = customer.id
        self.first_name = customer.first_name
        self.last_name = customer.last_name
        self.address = customer.address
        self.city = customer.city
        self.postal_code = customer.postal_code
        self.birthday = customer.birthday
        self.national_id = customer.national_id
        self.telephone_country_code = customer.country_details.telephone_country_code
        self.telephone = customer.telephone
        self.email = customer.email
        self.country_code = customer.country_details.name
        self.country = customer.country_details.name

    def to_dict(self):
        """ Converts api model instance into a dictionary """
        return {
            "id": self.id,
            "first name": self.first_name,
            "last name": self.last_name,
            "address": self.address,
            "city": self.city,
            "postal code": self.postal_code,
            "birthday": self.birthday,
            "national id": self.national_id,
            "telephone country code": self.telephone_country_code,
            "telephone": self.telephone,
            "email": self.email,
            "country_code": self.country_code,
            "country": self.country
        }