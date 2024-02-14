import random
from datetime import datetime, date
from datetime import timedelta
from decimal import Decimal
from faker import Faker
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

from business_logic.constants import (
    TelephoneCountryCodes,
    TransactionTypes,
    BusinessConstants,
    AccountTypes,
    UserRoles
    )

from models import (
    db,
    Role,
    User,
    Customer,
    Account,
    Transaction,
    Country
)

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

def seed_roles(db, user_datastore):
    existing_roles = [user_role.name for user_role in Role.query.all()]
    seed_roles = [role.value for role in UserRoles]

    for seed_role in seed_roles:
        if seed_role not in existing_roles:
            user_datastore.create_role(name=seed_role)

    db.session.commit()

def seed_users(db, user_datastore):
    existing_user_emails = [user.email for user in User.query.all()]
    SEED_USERS = [
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

    for seed_user in SEED_USERS:
        if seed_user["email"] not in existing_user_emails:
            user_datastore.create_user(
                email=seed_user["email"],
                password=hash_password(seed_user["password"]),
                roles=[seed_user["role"]],
                active=True
                )
    db.session.commit()

def seed_data(db):
    AVG_SALARY = 3500000
    SEED_AMOUNT_CUSTOMERS = 50

    existing_national_ids = [customer.national_id for customer in Customer.query.all()]

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
        # ensure right age of customer generated
        customer.birthday = fake.date_of_birth(
            minimum_age=BusinessConstants.MINIMUM_AGE,
            maximum_age=BusinessConstants.MAXIMUM_AGE)
        # ensure unique national ids are generated
        while True:
            customer.national_id = fake.ssn().replace("-", "")
            if customer.national_id not in existing_national_ids:
                existing_national_ids.append(customer.national_id)
                break
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
            account.balance = 0 #is this ok?? is not set by a transaction

            # start every new account with a deposit
            initial_deposit = Transaction()
            initial_deposit.timestamp = fake.date_time_between(
                start_date=account.created,
                end_date=account.created + timedelta(days=1))
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
