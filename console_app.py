from decimal import Decimal
from datetime import datetime, timedelta
from flask_mail import Message
from prettytable import PrettyTable
import sched, time

from extensions import mail
from app import create_app
from models import Country, Transaction
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
        flagged_customers:list[dict] = []
        customers = customer_service.get_all_customers_for_country(country)
        
        for customer in customers:
            # Sets needed to deduplicate entries
            flagged_transaction_ids = set()
            flagged_account_ids = set()
            
            # Check first rule
            transactions = transaction_service.get_transactions_for_customer_on_date(customer, yesterday)
            for transaction in transactions:
                if single_transaction_amount_exceeds_limit(transaction):
                    flagged_transaction_ids.add(transaction.id)
                    flagged_account_ids.add(transaction.account_id)

            # Check second rule
            if recent_transactions_exceeds_limit(customer):
                summed_transactions = transaction_service.get_summed_transactions(customer, TIME_PERIOD)

                for transaction in summed_transactions:
                    flagged_transaction_ids.add(transaction.id)
                    flagged_account_ids.add(transaction.account_id)

            # Add customer only if they have any flagged transactions
            if flagged_transaction_ids:
                flagged_customers.append({customer.id:
                                          {"transactions": flagged_transaction_ids,
                                           "accounts": flagged_account_ids}}
                                        )

        if flagged_customers:
            recipient = f"{country.name}@testbanken.se"

            msg = Message("Suspicious transactions found at "
                          + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                          sender="bank@bank.com", recipients=[recipient])
            
            customers_table = compose_message_table(flagged_customers,"Flagged customers found: ")

            msg.body = customers_table
            mail.send(msg)

    schedule_audit(scheduler)

def single_transaction_amount_exceeds_limit(transaction:Transaction):
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

def compose_message_table(flagged_entities:list[dict], message_header) -> None:
    table_data = []
    for flagged_entitiy in flagged_entities:
        for customer_id, flagged_accounts_transactions in flagged_entitiy.items():
            customer = customer_service.get_customer_accounts_country(customer_id)
            customer_data = {
                "account_holder_id": customer.id,
                "account_holder_first_name": customer.first_name,
                "account_holder_last_name": customer.last_name,
                "account_numbers": [account_id for account_id
                                    in flagged_accounts_transactions["accounts"]],
                "transaction_numbers": [transaction_id 
                                        for transaction_id
                                        in flagged_accounts_transactions["transactions"]]
            }
            table_data.append(customer_data)
    
    table = PrettyTable()
    table.field_names = ["Id", "Name", "Account number(s)", "Transaction number(s)"]    
    for data in table_data:
        message_row = [
            data["account_holder_id"],
            f"{data['account_holder_first_name']} {data['account_holder_last_name']}",
            ", ".join(str(account_number) for account_number in data["account_numbers"]),
            ", ".join(str(transaction_number) for transaction_number in data["transaction_numbers"])
        ]
        table.add_row(message_row)
    table.align["Transaction number(s)"] = "l"

    return message_header + "\n" + table.get_string() + "\n"

def schedule_audit(scheduler=None):
    """Schedules an audit for next midnight"""
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
        # audit_transactions()
        schedule_audit()