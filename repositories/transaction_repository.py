from decimal import Decimal
from datetime import datetime, timedelta
from models import db, Customer, Account, Transaction, Country
from sqlalchemy import select, func, desc, between
from sqlalchemy.orm import joinedload
from business_logic.constants import TransactionTypes


class TransactionRepository():
    def execute_transaction(account, amount: Decimal, transaction_type):
        transaction = Transaction()
        transaction.amount = amount
        transaction.timestamp = datetime.now()
        transaction.new_balance = account.balance + amount
        transaction.account_id = account.id
        transaction.type = transaction_type.value

        account.balance = transaction.new_balance
        
        db.session.add(transaction)
        db.session.commit()
    
    def get_limited_offset_transactions(account_id, limit, offset):
        return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).limit(limit).offset(offset).all()
        
    def get_count_of_transactions(account_id):
        return Transaction.query.filter_by(account_id=account_id).count()
    
    def get_sum_recent_transactions_of_country(customer: Customer, time_period: timedelta):
        from_date = datetime.now() - time_period
        
        return db.session.execute(
            select(func.sum(Transaction.amount)
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .group_by(Customer.id)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
        ).scalar()

    def get_summed_transaction_ids(customer: Customer, time_period: timedelta):
        from_date = datetime.now() - time_period
        
        return db.session.execute(
            select(Transaction.id
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
        ).scalars().all()

    def get_recent_unchecked_transactions_for(customer: Customer, from_datetime) -> list[Transaction]:
        return db.session.execute(
            select(Transaction)
            .join(Account, Account.id==Transaction.account_id)
            .join(Customer, Customer.id==Account.customer_id)
            .join(Country, Country.country_code==Customer.country)
            .where(Customer.id==customer.id)
            .where(Transaction.timestamp>=from_datetime)
            .where(Transaction.checked==False)
            .order_by(desc(Transaction.timestamp))
        ).scalars().all()