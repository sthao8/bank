from models import Account
from utils import format_money


class AccountRepository():
    def get_account_or_404(account_id: int):
        return Account.query.filter_by(id=account_id).one_or_404()

    def get_account_choices(customer):
        return [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
