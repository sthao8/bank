from models import Account, db

class AccountRepository():
    def get_account_from_id(self, account_id :int, raise_404 :bool=False):
        """get account from id, use raise_404 to show 404 if account doesn't exist"""
        query = Account.query.filter_by(id=account_id)
        if raise_404:
            return query.one_or_404()
        else:
            return query.one_or_none()
    
    def create_account_for_customer(self, account_information: dict):
        """Creates a new account from account_information dict,
        which should hold all the attributes needed for a new account"""
        new_account = Account()
        for attribute_name, value in account_information.items():
            setattr(new_account, attribute_name, value)

        db.session.add(new_account)
        db.session.commit()