from decimal import Decimal
from datetime import datetime
from models import db, Customer, Account, Transaction, Country
from sqlalchemy import select, func, desc, between
from constants.constants import TransactionTypes


class TransactionRepository():
    def execute_transaction(self, account: Account, amount: Decimal, transaction_type: TransactionTypes, new_balance: Decimal):
        transaction = Transaction()
        transaction.amount = amount
        transaction.timestamp = datetime.now()
        transaction.new_balance = new_balance
        transaction.account_id = account.id
        transaction.type = transaction_type.value

        account.balance = transaction.new_balance
        
        db.session.add(transaction)
        db.session.commit()
    
    def get_limited_offset_transactions(self, account_id: int, limit: int, offset: int):
        return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).limit(limit).offset(offset).all()

    def get_count_of_transactions(self, account_id):
        return Transaction.query.filter_by(account_id=account_id).count()
    
    def get_sum_recent_transactions_of_country(self, customer: Customer, from_date: datetime):
        return db.session.execute(
            select(func.sum(Transaction.amount)
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .group_by(Customer.id)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
        ).scalar()

    def get_summed_transaction_ids(self, customer: Customer, from_date: datetime):
        return db.session.execute(
            select(Transaction.id
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
        ).scalars().all()

    def get_recent_unchecked_transactions_for(self, customer: Customer, from_date) -> list[Transaction]:
        return db.session.execute(
            select(Transaction)
            .join(Account, Account.id==Transaction.account_id)
            .join(Customer, Customer.id==Account.customer_id)
            .join(Country, Country.country_code==Customer.country)
            .where(Customer.id==customer.id)
            .where(func.date(Transaction.timestamp)==from_date)
            .order_by(desc(Transaction.timestamp))
        ).scalars().all()