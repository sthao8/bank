import random
from datetime import datetime, date
from datetime import timedelta
from decimal import Decimal
from faker import Faker
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from business_logic.constants import (
    TelephoneCountryCodes,
    TransactionTypes,
    BusinessConstants,
    AccountTypes
    )


db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = "Countries"

    country_code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    telephone_country_code = db.Column(db.String(5), unique=False, nullable=False)

    customers = db.relationship("Customer", backref="country_details", lazy=True)

class Customer(db.Model):
    __tablename__= "Customers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), unique=False, nullable=False)
    last_name = db.Column(db.String(50), unique=False, nullable=False)
    address = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    postal_code = db.Column(db.String(10), unique=False, nullable=False)
    birthday = db.Column(db.Date, unique=False, nullable=False)
    national_id = db.Column(db.String(20), unique=False, nullable=False)
    telephone = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    country = db.Column(db.String(2), db.ForeignKey("Countries.country_code"), nullable=False)

    accounts = db.relationship("Account", backref="customer", lazy=True)

class Account(db.Model):
    __tablename__ = "Accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(10), unique=False, nullable=False)
    created = db.Column(db.Date, unique=False, nullable=False)
    balance = db.Column(db.Numeric(15, 2), unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"), nullable=False)

    transactions = db.relationship("Transaction", backref="account", lazy=True)

class Transaction(db.Model):
    __tablename__ = "Transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), unique=False, nullable=False)
    timestamp = db.Column(db.DateTime, unique=False, nullable=False)
    amount = db.Column(db.Numeric(15, 2), unique=False, nullable=False)
    new_balance = db.Column(db.Numeric(15,2), unique=False, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("Accounts.id"), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), unique=False,nullable=True)
    role = db.Column(db.String(7), unique=False, nullable=True)

def seed_countries(db):
    existing_telephone_country_codes = [country.telephone_country_code for country in Country.query.all()]

    for country_code in TelephoneCountryCodes:
        if country_code.value not in existing_telephone_country_codes:
            fake = Faker(country_code.name)
            country = Country()
            country.country_code = fake.current_country_code()
            country.name = fake.current_country()
            country.telephone_country_code = country_code.value
            db.session.add(country)
            db.session.commit()

def seed_users(db):
    existing_user_emails = [user.email for user in User.query.all()]
    seed_users = [
        {
            "email": "stefan.holmberg@systementor.se",
            "password": "Hejsan123#",
            "role": "admin"
        },
        {
            "email": "stefan.holmberg@nackademin.se",
            "password": "Hejsan123#",
            "role": "cashier"
        }
    ]

    for seed_user in seed_users:
        if seed_user["email"] not in existing_user_emails:
            new_user = User()
            new_user.email = seed_user["email"]
            new_user.password = seed_user["password"]
            new_user.role = seed_user["role"]

            db.session.add(new_user)
            db.session.commit()

def seed_data(db):
    AVG_SALARY = 3500000
    SEED_AMOUNT_CUSTOMERS = 50

    amount_users =  Customer.query.count()
    while amount_users < SEED_AMOUNT_CUSTOMERS:
        # generate customer details based on random supported locale
        random_locale = random.choice(BusinessConstants.SUPPORTED_LOCALES)
        fake = Faker(random_locale)

        customer = Customer()

        customer.first_name = fake.first_name()
        customer.last_name = fake.last_name()
        customer.address = fake.street_address()
        customer.postal_code = fake.postcode()
        customer.city = fake.city()
        customer.country = fake.current_country_code()
        customer.birthday = fake.date_of_birth(minimum_age=BusinessConstants.MINIMUM_AGE, maximum_age=BusinessConstants.MAXIMUM_AGE)
        customer.national_id = fake.ssn()
        customer.telephone = fake.phone_number()
        customer.email = fake.email()

        # generate between 1 and 4 random accounts for each user
        for _ in range(random.randint(1,4)):
            account = Account()

            account.account_type = random.choice(list(AccountTypes)).value

            # create random account open date between today and min age customer can open bank account
            AVG_WEEKS_PER_YEAR = 52.1775
            WEEKS_IN_MINMUM_AGE = int(BusinessConstants.MINIMUM_AGE * AVG_WEEKS_PER_YEAR)
            min_account_open_date = customer.birthday + timedelta(weeks=WEEKS_IN_MINMUM_AGE)

            if min_account_open_date < BusinessConstants.BANK_ESTABLISHED_DATE:
                min_account_open_date = BusinessConstants.BANK_ESTABLISHED_DATE

            account.created = fake.date_between(start_date=min_account_open_date)
            account.balance = 0

            # start every new account with a deposit
            initial_deposit = Transaction()
            initial_deposit.timestamp = fake.date_time_between(start_date=account.created, end_date=account.created) #TODO this didn't generate any datetime
            initial_deposit.amount = Decimal(random.randint(10000, 100000) / 100)
            initial_deposit.type = TransactionTypes.DEBIT.value
            account.balance = initial_deposit.amount

            initial_deposit.new_balance = account.balance
            account.transactions.append(initial_deposit)
            db.session.add(initial_deposit)

            previous_transaction_date = initial_deposit.timestamp


            # generate between 0 and 30 random transactions per account
            for _ in range(random.randint(0,30)):
                transaction = Transaction()

                transaction.timestamp = fake.date_time_between(start_date=previous_transaction_date)
                transaction.amount = Decimal(random.randint(1, AVG_SALARY) / 100)
                previous_transaction_date = transaction.timestamp

                # if transaction amount would drop balance below 0, make sure it's a debit
                if account.balance - transaction.amount < 0:
                    transaction.type = TransactionTypes.DEBIT.value
                else:
                    transaction.type = random.choice(list(TransactionTypes)).value

                if transaction.type == TransactionTypes.DEBIT.value:
                    account.balance = account.balance + transaction.amount
                else:
                    account.balance = account.balance - transaction.amount

                transaction.new_balance = account.balance
                account.transactions.append(transaction)
                db.session.add(transaction)

            customer.accounts.append(account)
            db.session.add(account)

        db.session.add(customer)
        db.session.commit()

        amount_users += 1
