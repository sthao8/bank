from decimal import Decimal
from datetime import timedelta, datetime, date
from flask_mail import Message
from extenstions import mail

from models import Country, Transaction, db
from services.country_services import CountryService, CountryRepository
from services.customer_services import CustomerService, CustomerRepository
from services.transaction_services import TransactionService, TransactionRepository

country_service = CountryService(CountryRepository)
customer_service = CustomerService(CustomerRepository)
transaction_service = TransactionService(TransactionRepository)

def main():
    countries:list[Country] = country_service.get_all_countries()
    from_datetime = datetime.now() - timedelta(hours=24)

    for country in countries:
        suspicious_transactions = []
        suspicious_customers = []
        customers = customer_service.get_all_customers_for(country)
        for customer in customers:
            if recent_transactions_exceeds_limit(customer):
                suspicious_customers.append(customer)

            transactions = transaction_service.get_recent_unchecked_transactions_for(customer, from_datetime)
            for transaction in transactions:
                if single_transaction_amount_exceeds_limit(transaction):
                    suspicious_transactions.append(transaction)
                else:
                    transaction.checked = True

            db.session.commit()

        #send report here
        #TODO SET UP MAIL
        print(suspicious_transactions)
        if suspicious_customers or suspicious_transactions:
            recipient = f"{country.name}@testbanken.se"
            msg = Message("suspicious transactions found" + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), sender="bank@bank.com", recipients=[recipient])
            
            msg.body = compose_message(suspicious_transactions, suspicious_customers)
            mail.send(msg)

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

def compose_message(transactions, customers):
    message_data = []
    TIME_PERIOD = timedelta(hours=72)

    
    if transactions:
        for transaction in transactions:
            customer = customer_service.get_customer_from_transaction(transaction)
            transaction_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_holder__last_name": customer.last_name,
                "account_number": transaction.account_id,
                "transaction_numbers": transaction.id
            }
            message_data.append(transaction_data)
    if customers:
        for customer in customers:
            transaction_ids = transaction_service.get_summed_transaction_ids(customer, TIME_PERIOD)
            customer_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_number": transaction.account_id,
                "transaction_numbers": transaction_ids
            }
            message_data.append(customer_data)
    
    message_header = f"Suspicious transactions found: \n"
    data_headers = "Account holder id | Account holder name | Account number | Transaction number(s) \n"
    for data in message_data:
        message_row = f"""{data["account_holder_id"]} | {data["account_holder_first_name"] + "" + data["account_holder_last_name"]} | {data["account_number"]} | {data["transaction_numbers"]} \n 
        """
    return message_header + data_headers + data

if __name__ == "__main__":
    main()