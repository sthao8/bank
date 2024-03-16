from datetime import date
from flask import render_template, flash, Blueprint, request

from forms import TransactionForm
from services.transaction_services import TransactionService
from repositories.transaction_repository import TransactionRepository
from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository
from constants.constants import TransactionTypes
from utils import get_first_error_message

from services.customer_services import CustomerService, CustomerRepository
from services.account_services import AccountService, AccountRepository
from services.transaction_services import TransactionService, TransactionRepository


account_repo = AccountRepository()
account_service = AccountService(account_repo)

customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo, account_service)

transaction_repo = TransactionRepository()
transaction_service = TransactionService(transaction_repo, account_service)

transactions_blueprint = Blueprint("transactions", __name__)

@transactions_blueprint.route("/transactions", methods=["GET", "POST"])
def transactions():
    form = TransactionForm()
    form.type.choices = [type.value for type in TransactionTypes] + ["transfer"]
    current_date = date.today()
    print(form.amount.data)

    if form.validate_on_submit():
        account_id = form.from_account.data
        to_account = form.to_account.data
        transaction_type_name = form.type.data
        amount = form.amount.data

        try:
            result = transaction_service.initiate_transaction_process(
                account_id,
                amount,
                transaction_type_name,
                to_account)
        except (ValueError, KeyError) as error:
            flash(error)
        else:
            flash(f"{transaction_type_name} success")
            return render_template("transactions/transaction_confirmation.html",
                                   transaction_type_name=transaction_type_name,
                                   result=result)
    elif request.method == "POST":
        flash(get_first_error_message(form.errors))
    return render_template("transactions/transactions.html",
                           active_page="transactions",
                           form=form,
                           current_date=current_date)
