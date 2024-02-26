from decimal import Decimal
from datetime import datetime, timedelta
from flask_mail import Message
from extenstions import mail
from prettytable import PrettyTable
import sched, time

from app import create_app
from models import Country, Transaction, db
from services.country_services import CountryService, CountryRepository
from services.customer_services import CustomerService, CustomerRepository
from services.transaction_services import TransactionService, TransactionRepository

country_service = CountryService(CountryRepository)
customer_service = CustomerService(CustomerRepository)
transaction_service = TransactionService(TransactionRepository)

TIME_PERIOD = timedelta(hours=72)

def audit_transactions(scheduler=None):
    countries:list[Country] = country_service.get_all_countries()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    for country in countries:
        suspicious_transactions = []
        suspicious_customers = []
        customers = customer_service.get_all_customers_for(country)
        
        for customer in customers:
            if recent_transactions_exceeds_limit(customer):
                suspicious_customers.append(customer)

            transactions = transaction_service.get_transactions_for(customer, yesterday)
            for transaction in transactions:
                if single_transaction_amount_exceeds_limit(transaction):
                    suspicious_transactions.append(transaction)
                transaction.checked = True

            db.session.commit()

        recipient = f"{country.name}@testbanken.se"

        if suspicious_customers or suspicious_transactions:
            msg = Message("Suspicious transactions found at " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), sender="bank@bank.com", recipients=[recipient])
            
            msg.body = compose_message(suspicious_transactions, suspicious_customers)
            mail.send(msg)
        else:
            msg = Message("No suspicious transactions found at " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), sender="bank@bank.com", recipients=[recipient])
            
            msg.body = "No transactions found"
            mail.send(msg)

    schedule_audit(scheduler)

def single_transaction_amount_exceeds_limit(transaction: Transaction):
    LIMIT = Decimal(15000)
    if transaction.amount > LIMIT:
        return True
    return False

def recent_transactions_exceeds_limit(customer):
    LIMIT = Decimal(23000)

    sum_recent_transactions = transaction_service.get_sum_recent_transactions_of(customer, TIME_PERIOD)
    if sum_recent_transactions > LIMIT:
        return True
    return False

def compose_message(transactions, customers):
    message_data = []

    if transactions:
        for transaction in transactions:
            customer = customer_service.get_customer_from_transaction(transaction)
            transaction_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_holder_last_name": customer.last_name,
                "account_numbers": [transaction.account_id],
                "transaction_numbers": [transaction.id]
            }
            message_data.append(transaction_data)
    if customers:
        for customer in customers:
            transaction_ids = transaction_service.get_summed_transaction_ids(customer, TIME_PERIOD)
            customer_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_holder_last_name": customer.last_name,
                "account_numbers": [account.id for account in customer.accounts],
                "transaction_numbers": transaction_ids
            }
            message_data.append(customer_data)
    
    table = PrettyTable()
    table.field_names = ["Id", "Name", "Account number(s)", "Transaction number(s)"]    
    for data in message_data:
        message_row = [
            data["account_holder_id"],
            f"{data['account_holder_first_name']} {data['account_holder_last_name']}",
            ", ".join(str(item) for item in data["account_numbers"]),
            ", ".join(str(item) for item in data["transaction_numbers"])
        ]
        table.add_row(message_row)
    table.align["Transaction number(s)"] = "l"

    # TODO: you may want to do also an html of this list
    message_header = f"Suspicious transactions found for customers: \n"

    return message_header + table.get_string()

def schedule_audit(scheduler=None):
    if not scheduler:
        s = sched.scheduler(time.time, time.sleep)

    tomorrow = datetime.now() + timedelta(days=1)
    next_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight_timestamp = next_midnight.timestamp()

    # Pass the same scheduler into the function call so we are not making a new scheduler each time
    s.enterabs(next_midnight_timestamp, priority=1, action=lambda: audit_transactions(scheduler))

    s.run()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        audit_transactions()
        schedule_audit()