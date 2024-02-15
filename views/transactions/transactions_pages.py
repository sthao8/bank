from datetime import date
from flask import render_template, flash, redirect, url_for, Blueprint, request
from flask_security import roles_accepted

from models import Account, db
from views.forms import PrefixedForm, TransactionForm, TransferForm, FlaskForm
from .services import (
    get_customer_or_404,
    get_account_or_404,
    execute_transaction,
    update_account_balance,
    get_account_choices)
from business_logic.constants import TransactionTypes
from utils import format_money

transactions_blueprint = Blueprint("transactions", __name__)


@transactions_blueprint.route("/transactions", methods=["POST"])
@roles_accepted("cashier")
def transactions():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_or_404(customer_id)
    form: PrefixedForm = TransactionForm()
    form.trans_type.choices = ["withdraw", "deposit"]
    accounts_labels = [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
    form.trans_accounts.choices = accounts_labels
    current_date = date.today()

    return render_template("transactions/withdraw_deposit.html", active_page="transaction", form=form, current_date=current_date, customer=customer)
    
@transactions_blueprint.route("/process-transaction", methods=["POST"])
@roles_accepted("cashier")
def process_transaction():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_or_404(customer_id)
    
    form = TransactionForm()
    form: PrefixedForm = TransactionForm()
    form.trans_type.choices = ["withdraw", "deposit"]
    form.trans_accounts.choices = get_account_choices(customer)

    account: Account = get_account_or_404(int(form.trans_accounts.data))
    
    if form.validate_on_submit():

        amount = form.trans_amount.data

        if form.trans_type.data == "withdraw":
            transaction_type = TransactionTypes.WITHDRAW.value
            if amount > account.balance:
                flash("ERROR: Insufficient funds for requested transaction!")
                return redirect(url_for("customers.customer_page", customer_id=customer.id))
        elif form.trans_type.data == "deposit":
            transaction_type = TransactionTypes.DEPOSIT.value

        execute_transaction(account, amount, transaction_type)

        flash(f"success! {form.trans_type.data} money in account number {account.id}.")
        return redirect(url_for("customers.customer_page", customer_id=customer.id))
    flash("didn't pass validation")
    return redirect(url_for("customers.customer_page"), customer_id=customer.id)

@transactions_blueprint.route("/transfer", methods=["POST"])
@roles_accepted("cashier")
def transfer():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_or_404(customer_id)
    form: FlaskForm = TransferForm()
    current_date = date.today()

    accounts_choices = get_account_choices(customer)
    form.transfer_account_from.choices = accounts_choices
    form.transfer_account_to.choices = accounts_choices

    return render_template("transactions/transfer.html", active_page="transfer", customer=customer, form=form, current_date=current_date)
    
@transactions_blueprint.route("/process-transfer", methods=["POST"])
@roles_accepted("cashier")
def process_transfer():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_or_404(customer_id)
    form: FlaskForm = TransferForm()
    current_date = date.today()

    accounts_choices = get_account_choices(customer)
    form.transfer_account_from.choices = accounts_choices
    form.transfer_account_to.choices = accounts_choices

    if form.validate_on_submit():
        from_account = get_account_or_404(form.transfer_account_from.data)
        to_account = get_account_or_404(form.transfer_account_to.data)
        amount = form.transfer_amount.data

        if amount < from_account.balance:
            execute_transaction(from_account, amount, TransactionTypes.WITHDRAW.value)
            execute_transaction(to_account, amount, TransactionTypes.DEPOSIT.value)

            flash(f"Success! Transferred {amount} from account no. {from_account} to account no. {to_account}!")
        else:
            flash("ERROR: Insufficient funds for requested transaction!")
    else:
        flash("Did not pass validation")
    return redirect(url_for("customers.customer_page", customer_id=customer.id))
