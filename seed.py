import random
from datetime import timedelta, datetime, date
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

MAX_TRANSACTION_AMOUNT = 2400000
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
    existing_national_ids = {customer.national_id for customer in Customer.query.all()}

    count_users =  Customer.query.count()

    while count_users < SEED_AMOUNT_CUSTOMERS:
        # generate customer details based on random supported locale
        random_locale = random.choice(BusinessConstants.SUPPORTED_LOCALES)
        fake: Faker = Faker(random_locale)

        customer = create_customer(fake, existing_national_ids)
        existing_national_ids.add(customer.national_id)

        # generate between 1 and 4 random accounts for each user
        for _ in range(random.randint(1,4)):
            account = create_account_for_customer(fake, customer)

            # start every new account with a random deposit soon after
            initial_deposit_amount = Decimal(random.randint(10000, 100000) / 100)
            initial_deposit_timestamp = fake.date_time_between(
                start_date=account.created,
                end_date=account.created + timedelta(days=1))
            account.balance = calculate_new_balance(account, initial_deposit_amount, TransactionTypes.DEPOSIT.value)
            initial_deposit = create_transaction_for_account(
                initial_deposit_timestamp,
                TransactionTypes.DEPOSIT.value,
                initial_deposit_amount,
                account.balance)

            account.transactions.append(initial_deposit)
            db.session.add(initial_deposit)

            previous_transaction_datetime = initial_deposit.timestamp

            # generate between 0 and 30 random transactions per account
            for _ in range(random.randint(0,30)):
                transaction_timestamp = fake.date_time_between(start_date=previous_transaction_datetime)
                amount = Decimal(random.randint(1, MAX_TRANSACTION_AMOUNT) / 100)
                transaction_type = choose_random_transaction_type(account.balance, amount)
                account.balance = calculate_new_balance(account, amount, transaction_type)

                transaction = create_transaction_for_account(
                    transaction_timestamp,
                    transaction_type,
                    amount,
                    account.balance
                )

                account.transactions.append(transaction)
                db.session.add(transaction)

                # Don't seed more than one transaction with today's date
                previous_transaction_datetime = transaction.timestamp
                if previous_transaction_datetime.date() == date.today():
                    break

            customer.accounts.append(account)
            db.session.add(account)

        db.session.add(customer)
        db.session.commit()

        count_users += 1

def create_customer(fake: Faker, existing_national_ids) -> Customer:
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
                break
        customer.telephone = fake.phone_number()
        customer.email = fake.email()

        return customer

def create_account_for_customer(fake: Faker, customer: Customer):
    AVG_WEEKS_PER_YEAR = 52.1775
    WEEKS_IN_MINMUM_AGE = int(BusinessConstants.MINIMUM_AGE * AVG_WEEKS_PER_YEAR)
    account = Account()

    account.account_type = random.choice(list(AccountTypes)).value

    # if min account open date would fall before bank established, set that as min
    min_account_open_date = customer.birthday + timedelta(weeks=WEEKS_IN_MINMUM_AGE)
    if min_account_open_date < BusinessConstants.BANK_ESTABLISHED_DATE:
        min_account_open_date = BusinessConstants.BANK_ESTABLISHED_DATE

    account.created = fake.date_between(start_date=min_account_open_date)
    account.balance = 0
    
    return account

def create_transaction_for_account(timestamp:datetime, transaction_type: str, amount: Decimal, new_account_balance: Decimal):
    transaction = Transaction()
    transaction.timestamp = timestamp
    transaction.amount = amount
    transaction.type = transaction_type
    transaction.new_balance = new_account_balance

    return transaction

def calculate_new_balance(account: Account, amount: Decimal, transaction_type: str):
    if transaction_type == TransactionTypes.DEPOSIT.value:
        return account.balance + amount
    else:
        return account.balance - amount
    
def choose_random_transaction_type(account_balance, amount):
# if transaction amount would drop balance below 0, make sure it's a deposit
    if account_balance - amount < 0:
        return TransactionTypes.DEPOSIT.value
    else:
        return random.choice(list(TransactionTypes)).value