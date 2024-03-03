from decimal import Decimal
from datetime import datetime, date
from models import db, Customer, Account, Transaction, Country
from sqlalchemy import select, func, desc, between
from constants.constants import TransactionTypes


class TransactionRepository():
    def execute_transaction(
            self,
            account: Account,
            amount: Decimal,
            transaction_type: TransactionTypes,
            new_balance: Decimal
            ) -> Transaction:
        """Executes a transaction, returning the transaction"""
        transaction = Transaction()
        transaction.amount = amount
        transaction.timestamp = datetime.now()
        transaction.new_balance = new_balance
        transaction.account_id = account.id
        transaction.type = transaction_type.value

        account.balance = transaction.new_balance
        
        db.session.add(transaction)
        db.session.commit()

        return transaction
    
    def get_limited_offset_transactions(self,
                                        account_id: int,
                                        limit: int,
                                        offset: int
                                        ) -> list[Transaction]:
        """Get transactions for an account, applying provided limit and offset"""
        return (Transaction.query
                .filter_by(account_id=account_id)
                .order_by(Transaction.timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all())

    def get_count_of_transactions(self, account_id) -> int:
        """Returns count of transactions for an account"""
        return Transaction.query.filter_by(account_id=account_id).count()
    
    def get_sum_recent_transactions_of_country(
            self,
            customer: Customer,
            from_date: datetime
            ) -> Decimal:
        """Get the sum of all transactions from a from_date to now"""
        return db.session.execute(
            select(func.sum(Transaction.amount)
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
                   .group_by(Customer.id)
        ).scalar()

    def get_summed_transactions(self, customer: Customer, from_date: datetime) -> list[Transaction]:
        """Get all transactions for a customer from the from_date to now"""
        return db.session.execute(
            select(Transaction
                   ).join(Account, Account.id==Transaction.account_id)
                   .join(Customer, Customer.id==Account.customer_id)
                   .join(Country, Country.country_code==Customer.country)
                   .where(Customer.id==customer.id)
                   .where(between(Transaction.timestamp, from_date, datetime.now()))
        ).scalars().all()

    def get_recent_transactions_for_customer(self,
                                             customer: Customer,
                                             target_date: date
                                             ) -> list[Transaction]:
        """Get all transactions for a customer for a given date"""
        return db.session.execute(
            select(Transaction)
            .join(Account, Account.id==Transaction.account_id)
            .join(Customer, Customer.id==Account.customer_id)
            .join(Country, Country.country_code==Customer.country)
            .where(Customer.id==customer.id)
            .where(func.date(Transaction.timestamp)==target_date)
            .order_by(desc(Transaction.timestamp))
        ).scalars().all()