from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request, abort
from flask_security import login_required
from math import ceil

from models import db
from .services import (
    TransactionsApiModel,
    CustomerApiModel
    )
from views.forms import RegisterCustomerForm

from services.country_services import CountryService, CountryRepository
from services.transaction_services import TransactionService, TransactionRepository
from services.customer_services import CustomerService, CustomerRepository
from services.account_services import AccountService, AccountRepository

customers_blueprint = Blueprint("customers", __name__)

country_service = CountryService(CountryRepository)
customer_service = CustomerService(CustomerRepository)
transaction_service = TransactionService(TransactionRepository)
account_service = AccountService(AccountRepository)

@customers_blueprint.route("/", methods=["GET"])
@login_required
def index():
    country_stats = country_service.get_country_stats()

    global_stats = country_service.calculate_global_stats(country_stats)

    return render_template(
        "customers/index.html",
        active_page="index",
        country_stats=country_stats,
        global_stats=global_stats
    )

@customers_blueprint.route("/country-page/<country_name>", methods=["GET"])
@login_required
def country_page(country_name):
    country = country_service.get_country_or_404(country_name)

    country_customer = country_service.get_country_customer(country.name)
    
    return render_template(
        "customers/country_page.html",
        active_page="index",
        country=country.name,
        country_customers=country_customer)
    
@customers_blueprint.route("/register_customer", methods=["GET", "POST"])
@login_required
def register_customer():
    # TODO: do maybe some more validation stuff here

    form = RegisterCustomerForm()
    form.register_country.choices = country_service.get_form_country_choices()

    if form.validate_on_submit():
        try:
            new_customer = customer_service.create_customer_and_new_account(form)
        except ValueError as error:
            flash(f"ERROR: {error}")
        else:
            flash("Successfully added customer")
            return redirect(url_for("customers.customer_page", customer_id=new_customer.id))

    return render_template(
        "customers/register_customer.html",
        form=form,
        active_page="register_customer")

@customers_blueprint.route("/customer/<customer_id>", methods=["GET"])
@login_required
def customer_page(customer_id):
    customer = customer_service.get_customer_or_404(customer_id)
    
    total_balance = sum([account.balance for account in customer.accounts])
    return render_template(
        "customers/customer_page.html",
        customer=customer,
        total_balance=total_balance)

@customers_blueprint.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
    account = account_service.get_account_or_404(account_id)
    return render_template("customers/account_page.html", account=account)

@customers_blueprint.route("/api/accounts/<int:account_id>")
def transactions_api(account_id):
    account = account_service.get_account_or_404(account_id)

    # Make sure offset and limit are not negative
    offset = max(request.args.get("offset", 0, int), 0)
    limit = max(request.args.get("limit", 20, int), 1)

    total_transactions_amount = transaction_service.get_count_of_transactions(account_id)

    has_more = offset + limit < total_transactions_amount

    account_transactions = transaction_service.get_limited_offset_transactions(account_id, limit, offset)

    transactions_dict = [TransactionsApiModel(transaction).to_dict() for transaction in account_transactions]

    return jsonify({"transactions": transactions_dict, "has_more": has_more})

@customers_blueprint.route("/api/<int:customer_id>")
def customer_api(customer_id):
    customer = customer_service.get_customer_or_404(customer_id)

    customer_dict = CustomerApiModel(customer).to_dict()

    return jsonify(customer_dict)
