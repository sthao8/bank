from datetime import date
from flask import render_template, flash, redirect, url_for, Blueprint, request
from flask_security import roles_accepted

from models import Account, db
from views.forms import PrefixedForm, TransactionForm, TransferForm
from .services import get_customer_joined_accounts_from_id, get_account_from_id, create_transaction, update_account_balance
from business_logic.constants import TransactionTypes
from utils import format_money

transactions_blueprint = Blueprint("transactions", __name__)


@transactions_blueprint.route("/transactions", methods=["POST"])
@roles_accepted("cashier")
def transactions():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_joined_accounts_from_id(customer_id)
    if customer:
        form: PrefixedForm = TransactionForm()
        form.trans_type.choices = ["withdraw", "deposit"]
        accounts_labels = [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
        form.trans_accounts.choices = accounts_labels
        current_date = date.today()

        return render_template("transactions/transactions.html", active_page="transaction", form=form, current_date=current_date, customer=customer)
    else:
        flash("no such customer")
        return redirect(url_for("customers.index"))
    
@transactions_blueprint.route("/process-transaction", methods=["POST"])
@roles_accepted("cashier")
def process_transaction():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_joined_accounts_from_id(customer_id)
    
    form = TransactionForm()
    form: PrefixedForm = TransactionForm()
    form.trans_type.choices = ["withdraw", "deposit"]
    accounts_labels = [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
    form.trans_accounts.choices = accounts_labels

    account: Account = get_account_from_id(int(form.trans_accounts.data))
    
    if customer and account and form.validate_on_submit():

        amount = form.trans_amount.data

        if form.trans_type.data == "withdraw":
            transaction_type = TransactionTypes.WITHDRAW.value
            if amount > account.balance:
                flash("Cannot withdraw more than account balance")
                return redirect(url_for("customers.customer_page", customer_id=customer.id))
        elif form.trans_type.data == "deposit":
            transaction_type = TransactionTypes.DEPOSIT.value

        transaction = create_transaction(account, amount, transaction_type)
        update_account_balance(account, transaction)

        db.session.add(transaction)
        db.session.commit()

        flash(f"success! {form.trans_type.data} money in account number {account.id}.")
        return redirect(url_for("customers.customer_page", customer_id=customer.id))
    flash("didn't pass validation")
    return redirect(url_for("customers.customer_page"), customer_id=customer.id)

@transactions_blueprint.route("/transfer", methods=["POST"])
@roles_accepted("cashier")
def transfer():
    customer_id = request.form.get("customer_id", None)
    customer = get_customer_joined_accounts_from_id(customer_id)
    if customer:
        form = TransferForm()
        current_date = date.today()

        #TODO Not functional yet!!!
        return render_template(active_page="transfer", form=form, current_date=current_date)
    else:
        flash("no such customer")
        return redirect(url_for("customers.index"))