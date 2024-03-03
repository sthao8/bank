from models import Customer, Transaction, User

class TransactionsApiModel:
    def __init__(self, transaction: Transaction) -> None:
        self.id = transaction.id
        self.type = transaction.type
        self.timestamp = transaction.timestamp
        self.amount = transaction.amount
        self.new_balance = transaction.new_balance
        self.account_id = transaction.account_id

    def to_dict(self):
        """ Converts api model instance into a dictionary """
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "new_balance": self.new_balance,
            "account_id": self.account_id
        }

class CustomerApiModel:
    def __init__(self, customer: Customer) -> None:
        self.id = customer.id
        self.first_name = customer.first_name
        self.last_name = customer.last_name
        self.address = customer.address
        self.city = customer.city
        self.postal_code = customer.postal_code
        self.birthday = customer.birthday
        self.national_id = customer.national_id
        self.telephone_country_code = customer.country_details.telephone_country_code
        self.telephone = customer.telephone
        self.email = customer.email
        self.country_code = customer.country_details.country_code
        self.country = customer.country_details.name
        self.accounts = [
            {"account_number":account.id,
             "balance": account.balance,
             "account_type": account.account_type
             }
             for account in customer.accounts
            ]
        self.total_balance = sum([account["balance"] for account in self.accounts])

    def to_dict(self):
        """ Converts api model instance into a dictionary """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "birthday": self.birthday,
            "national_id": self.national_id,
            "telephone_country code": self.telephone_country_code,
            "telephone": self.telephone,
            "email": self.email,
            "country_code": self.country_code,
            "country": self.country,
            "accounts": self.accounts,
            "total_balance": self.total_balance
        }
  
class UserApiModel:
    def __init__(self, user: User) -> None:
        self.id = user.id
        self.email = user.email
        self.is_active = user.active
        self.role = user.roles[0]

    def to_dict(self):
        """ Converts api model instance into a dictionary """
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "role": self.role.name
        }
  