from decimal import Decimal
from datetime import timedelta, datetime, date

from models import Country, Transaction
from services.country_services import CountryService, CountryRepository
from services.customer_services import CustomerService, CustomerRepository
from services.transaction_services import TransactionService, TransactionRepository

country_service = CountryService(CountryRepository)
customer_service = CustomerService(CustomerRepository)
transaction_service = TransactionService(TransactionRepository)

def main():
    countries:list[Country] = country_service.get_all_countries()
    from_datetime = datetime.now() - timedelta(hours=24)
    suspicious_transactions = []

    for country in countries:
        customers = country_service.get_all_country_customers(country.name)
        for customer in customers:
            transactions = transaction_service.get_recent_unchecked_transactions_for(customer, from_datetime)
            for transaction in transactions:
                if single_transaction_amount_exceeds_limit(transaction):
                    # TODO turn transaction.checked to true
                    suspicious_transactions.append(transaction)
                else:
                    transaction.checked = True

            if recent_transactions_exceeds_limit(customer):
                suspicious_transactions.append(customer)
            
            db.session.commit()

        #send report here

def single_transaction_amount_exceeds_limit(transaction: Transaction):
    LIMIT = Decimal(15000)
    if transaction.amount > LIMIT:
        return True
    return False

def recent_transactions_exceeds_limit(customer):
    LIMIT = Decimal(23000)
    TIME_PERIOD = timedelta(hours=72)

    sum_recent_transactions = transaction_service.get_sum_recent_transactions_of(customer, TIME_PERIOD)
    if sum_recent_transactions > LIMIT:
        return True
    return False


if __name__ == "__main__":
    main()