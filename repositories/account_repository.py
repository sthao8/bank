from models import Account, db
from utils import format_money


class AccountRepository():
    def get_account_from_id(self, account_id: int, raise_404: bool = False):
        query = Account.query.filter_by(id=account_id)
        if raise_404:
            return query.one_or_404()
        else:
            return query.one_or_none()

    def get_account_choices(self, customer):
        return [
            (account.id, f"{account.id}: current balance: {format_money(account.balance)}")
            for account in customer.accounts
            ]
    
    def create_account_for_customer(self, account_information: dict):
        new_account = Account()
        for attribute_name, value in account_information.items():
            setattr(new_account, attribute_name, value)

        db.session.add(new_account)
        db.session.commit()

