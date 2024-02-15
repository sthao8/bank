from models import db, Customer, Account
from sqlalchemy import select

def get_customer_from_account_number(account_number):
    return db.session.execute(
        select(Customer)
        .join(Account, Customer.id==Account.id)
        .where(Customer.id==account_number)
        ).one_or_none()