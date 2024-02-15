from datetime import datetime
from models import db, Customer, Account, Transaction
from sqlalchemy.orm import joinedload
from business_logic.constants import TransactionTypes


def get_customer_joined_accounts_from_id(customer_id):
    return Customer.query.filter_by(id=customer_id).options(joinedload(Customer.accounts)).one_or_none()

def get_account_from_id(account_id: int):
    return Account.query.filter_by(id=account_id).one_or_none()

def create_transaction(account, amount, transaction_type):
    transaction = Transaction()
    transaction.amount = amount
    transaction.type = transaction_type
    transaction.timestamp = datetime.now()
    # TODO need to test this some more. math not working out right
    transaction.new_balance = account.balance + amount if transaction_type == TransactionTypes.DEPOSIT.value else account.balance - amount
    transaction.account_id = account.id

    return transaction

def update_account_balance(account, transaction):
    account.balance = transaction.new_balance