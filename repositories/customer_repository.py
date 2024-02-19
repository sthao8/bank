from datetime import datetime
from business_logic.constants import AccountTypes
from models import Customer, Account, db
from sqlalchemy.orm import joinedload

class CustomerRepository():
    def get_customer_or_none(customer_id):
        return Customer.query.filter_by(id=customer_id).one_or_none() 

    def get_customer_joined_accounts_country_or_404(customer_id):
        return Customer.query.filter_by(id=customer_id).options(
            joinedload(Customer.accounts),
            joinedload(Customer.country_details)
            ).one_or_404()
    
    def get_customer_from_national_id(national_id):
        return Customer.query.filter_by(national_id=national_id).one_or_none()
    
    def create_customer_and_new_account(form) -> Customer:
        new_customer = Customer()

        for field_name, field in form._fields.items():
            if field_name.startswith(form.field_prefix):
                model_col_name = form.get_column_name(field_name)
                setattr(new_customer, model_col_name, field.data)

        new_account = Account()
        new_account.account_type = AccountTypes.CHECKING.value
        new_account.created = datetime.now()
        new_account.balance = 0 # TODO: not sure about this. maybe all accounts should start with 0?
        new_customer.accounts.append(new_account)

        db.session.add(new_customer)
        db.session.commit()

        return new_customer