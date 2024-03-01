import random
from datetime import date
from datetime import timedelta
from decimal import Decimal
from faker import Faker
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

from constants.constants import (
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

SEED_USERS = [
        {
            "email": "stefan.holmberg@systementor.se",
            "password": "Hejsan123#",
            "role": UserRoles.ADMIN.value
        },
        {
            "email": "stefan.holmberg@nackademin.se",
            "password": "Hejsan123#",
            "role": UserRoles.CASHIER.value
        }
    ]

MAX_TRANSACTION_AMOUNT = 3000000
SEED_AMOUNT_CUSTOMERS = 5000

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
    seed_roles = [role.value for role in UserRoles]
    for role in seed_roles:
        user_datastore.find_or_create_role(name=role)
    db.session.commit()

def seed_users(db, user_datastore: SQLAlchemyUserDatastore):
    for seed_user in SEED_USERS:
        if not user_datastore.find_user(email=seed_user["email"]):
            user = user_datastore.create_user(
                email=seed_user["email"],
                password=hash_password(seed_user["password"]),
                roles=[seed_user["role"]],
                active=True
                )
    db.session.commit()

def seed_data(db: SQLAlchemy):
    AVG_WEEKS_PER_YEAR = 52.1775
    WEEKS_IN_MINMUM_AGE = int(BusinessConstants.MINIMUM_AGE * AVG_WEEKS_PER_YEAR)

    existing_national_ids = [customer.national_id for customer in Customer.query.all()]

    count_users =  Customer.query.count()

    while count_users < SEED_AMOUNT_CUSTOMERS:
        # generate customer details based on random supported locale
        random_locale = random.choice(BusinessConstants.SUPPORTED_LOCALES)
        fake: Faker = Faker(random_locale)

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
            # strip the dashes to get uniform/comparable numbers
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

            # if min account open date would fall before bank established, set that as min
            min_account_open_date = customer.birthday + timedelta(weeks=WEEKS_IN_MINMUM_AGE)
            if min_account_open_date < BusinessConstants.BANK_ESTABLISHED_DATE:
                min_account_open_date = BusinessConstants.BANK_ESTABLISHED_DATE

            account.created = fake.date_between(start_date=min_account_open_date)
            account.balance = 0

            # start every new account with a random deposit soon after
            initial_deposit = Transaction()
            initial_deposit.timestamp = fake.date_time_between(
                start_date=account.created,
                end_date=account.created + timedelta(days=1))
            initial_deposit.amount = Decimal(random.randint(10000, 100000) / 100)
            initial_deposit.type = TransactionTypes.DEPOSIT.value
            account.balance = initial_deposit.amount

            initial_deposit.new_balance = account.balance
            account.transactions.append(initial_deposit)
            db.session.add(initial_deposit)

            previous_transaction_datetime = initial_deposit.timestamp

            # generate between 0 and 30 random transactions per account
            for _ in range(random.randint(0,30)):
                transaction = Transaction()

                transaction.timestamp = fake.date_time_between(start_date=previous_transaction_datetime)
                transaction.amount = Decimal(random.randint(1, MAX_TRANSACTION_AMOUNT) / 100)

                previous_transaction_datetime = transaction.timestamp

                # if transaction amount would drop balance below 0, make sure it's a deposit
                if account.balance - transaction.amount < 0:
                    transaction.type = TransactionTypes.DEPOSIT.value
                else:
                    transaction.type = random.choice(list(TransactionTypes)).value

                if transaction.type == TransactionTypes.DEPOSIT.value:
                    account.balance = account.balance + transaction.amount
                else:
                    account.balance = account.balance - transaction.amount

                transaction.new_balance = account.balance
                account.transactions.append(transaction)
                db.session.add(transaction)

                # Don't seed more than one transaction with today's date
                if previous_transaction_datetime.date() == date.today():
                    break

            customer.accounts.append(account)
            db.session.add(account)

        db.session.add(customer)
        db.session.commit()

        count_users += 1
