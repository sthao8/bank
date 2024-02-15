from datetime import datetime
from models import db, Customer, Account, Transaction
from sqlalchemy.orm import joinedload
from business_logic.constants import TransactionTypes
from utils import format_money

def get_customer_or_404(customer_id):
    return Customer.query.filter_by(id=customer_id).options(joinedload(Customer.accounts)).one_or_404()

def get_account_or_404(account_id: int):
    return Account.query.filter_by(id=account_id).one_or_404()

def execute_transaction(account, amount, transaction_type):
    transaction = Transaction()
    transaction.amount = amount
    transaction.type = transaction_type
    transaction.timestamp = datetime.now()
    transaction.new_balance = account.balance + amount if transaction_type == TransactionTypes.DEPOSIT.value else account.balance - amount
    transaction.account_id = account.id

    account.balance = transaction.new_balance
    
    db.session.add(transaction)
    db.session.commit()

def update_account_balance(account, transaction):
    account.balance = transaction.new_balance

def get_account_choices(customer):
    return [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]

