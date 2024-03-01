from decimal import Decimal
from datetime import datetime, timedelta
from flask_mail import Message
from prettytable import PrettyTable
import sched, time

from extensions import mail
from app import create_app
from models import Country, Transaction, db
from services.country_services import CountryService, CountryRepository
from services.customer_services import CustomerService, CustomerRepository
from services.transaction_services import TransactionService, TransactionRepository
from services.account_services import AccountService, AccountRepository

country_repo = CountryRepository()
country_service = CountryService(country_repo)

account_repo = AccountRepository()
account_service = AccountService(account_repo)

customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo, account_service)

transaction_repo = TransactionRepository()
transaction_service = TransactionService(transaction_repo, account_service)

TIME_PERIOD = timedelta(hours=72)

def audit_transactions(scheduler=None):
    countries:list[Country] = country_service.get_all_countries()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    for country in countries:
        suspicious_transactions = []
        suspicious_customers = []
        customers = customer_service.get_all_customers_for(country)
        
        for customer in customers:
            customer_flagged_transactions = []
            if recent_transactions_exceeds_limit(customer): #TODO maybe this returns a list of all transactions accounted for
                suspicious_customers.append(customer)

            transactions = transaction_service.get_transactions_for(customer, yesterday)
            for transaction in transactions:
                if single_transaction_amount_exceeds_limit(transaction):
                    customer_flagged_transactions.append(transaction)
            
            if customer_flagged_transactions:
                suspicious_transactions.append(dict({customer.id:customer_flagged_transactions}))

        #TODO maybe export this into own function
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

def compose_message(flagged_transactions, customers):
    message_1_data = []
    # TODO make this function more general
    if flagged_transactions:
        for flagged_transaction in flagged_transactions:
            for customer_id, list_of_transactions in flagged_transaction.items():
                customer = customer_service.get_customer_or_404(customer_id)
                transaction_data = {
                    "account_holder_id": customer.id,
                    "account_holder_first_name": customer.first_name,
                    "account_holder_last_name": customer.last_name,
                    "account_numbers": set([transaction.account_id for transaction in list_of_transactions]),
                    "transaction_numbers": [transaction.id for transaction in list_of_transactions]
                }
                message_1_data.append(transaction_data)
    message_2_data = []
    if customers:
        for customer in customers:
            transaction_ids = transaction_service.get_summed_transaction_ids(customer, TIME_PERIOD)
            customer_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_holder_last_name": customer.last_name,
                "account_numbers": set([account.id for account in customer.accounts]),
                "transaction_numbers": transaction_ids
            }
            message_2_data.append(customer_data)
    
    table = PrettyTable()
    table.field_names = ["Id", "Name", "Account number(s)", "Transaction number(s)"]    
    for data in message_1_data:
        message_row = [
            data["account_holder_id"],
            f"{data['account_holder_first_name']} {data['account_holder_last_name']}",
            ", ".join(str(item) for item in data["account_numbers"]),
            ", ".join(str(item) for item in data["transaction_numbers"])
        ]
        table.add_row(message_row)
    table.align["Transaction number(s)"] = "l"

    table2 = PrettyTable()
    table2.field_names = ["Id", "Name", "Account number(s)", "Transaction number(s)"]    
    for data in message_2_data:
        message_row = [
            data["account_holder_id"],
            f"{data['account_holder_first_name']} {data['account_holder_last_name']}",
            ", ".join(str(item) for item in data["account_numbers"]),
            ", ".join(str(item) for item in data["transaction_numbers"])
        ]
        table2.add_row(message_row)
    table2.align["Transaction number(s)"] = "l"

    # TODO: you may want to do also an html of this list
    message_header = f"Flagged transactions violate rule 1: \n"
    message_header2 = f"Flagged transactions violate rule 2: \n"

    return message_header + table.get_string() + "\n" + message_header2 + table2.get_string()

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