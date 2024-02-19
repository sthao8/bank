from decimal import Decimal
from datetime import datetime
from models import db, Customer, Account, Transaction
from sqlalchemy.orm import joinedload
from business_logic.constants import TransactionTypes



class TransactionRepository():
    def create_transaction(account, amount: Decimal, transaction_type):
        transaction = Transaction()
        transaction.amount = amount
        transaction.timestamp = datetime.now()
        transaction.new_balance = account.balance + amount if transaction_type == TransactionTypes.DEPOSIT else account.balance - amount
        transaction.account_id = account.id
        transaction.type = transaction_type.value

        account.balance = transaction.new_balance
        
        db.session.add(transaction)
        db.session.commit()
    
    def get_limited_offset_transactions(account_id, transactions_per_page, page):
        offset_value = (page - 1) * transactions_per_page
        return Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).limit(transactions_per_page).offset(offset_value).all()
        
    def get_count_of_transactions(account_id):
        return Transaction.query.filter_by(account_id=account_id).count()
    
    