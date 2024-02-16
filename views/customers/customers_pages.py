from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request, abort
from flask_security import login_required
from math import ceil

from models import db
from .services import (
    get_customer_or_404,
    get_account_or_404,
    get_all_countries,
    create_customer_and_new_account,
    get_country_stats,
    get_country_customer,
    TransactionsApiModel,
    get_limited_offset_transactions,
    get_count_of_transactions,
    get_country_or_404
    )
from views.forms import RegisterCustomerForm

customers_blueprint = Blueprint("customers", __name__)

@customers_blueprint.route("/", methods=["GET"])
@login_required
def index():
    country_stats = get_country_stats()

    global_stats = {
        "number_of_customers": sum([country.number_of_customers for country in country_stats]),
        "number_of_accounts": sum([country.number_of_accounts for country in country_stats]),
        "sum_of_accounts": sum([country.sum_of_accounts for country in country_stats])
    }

    return render_template(
        "customers/index.html",
        active_page="index",
        country_stats=country_stats,
        global_stats=global_stats
    )

@customers_blueprint.route("/country-page/<country>", methods=["GET"])
@login_required
def country_page(country):
    country = get_country_or_404(country)

    country_customer = get_country_customer(country.name)
    
    return render_template(
        "customers/country_page.html",
        active_page="index",
        country=country.name,
        country_customers=country_customer)
    
@customers_blueprint.route("/register_customer", methods=["GET", "POST"])
@login_required
def register_customer():
    # TODO: do maybe some more validation stuff here

    countries = get_all_countries()
    form = RegisterCustomerForm()
    form.register_country.choices = [(country.country_code, country.name) for country in countries]

    if form.validate_on_submit():
        #TODO Here we gotta check for duplicate ssn

        new_customer = create_customer_and_new_account(form)
        db.session.add(new_customer)
        db.session.commit()

        flash("Successfully added customer")
        return redirect(url_for("customers.customer_page", customer_id=new_customer.id))

    return render_template(
        "customers/register_customer.html",
        form=form,
        active_page="register_customer")

@customers_blueprint.route("/customer/<customer_id>", methods=["GET"])
@login_required
def customer_page(customer_id):
    customer = get_customer_or_404(customer_id)
    
    total_balance = sum([account.balance for account in customer.accounts])
    return render_template(
        "customers/customer_page.html",
        customer=customer,
        total_balance=total_balance)

@customers_blueprint.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
    account = get_account_or_404(account_id)
    return render_template("customers/account_page.html", account=account)

@customers_blueprint.route("/api/accounts/<int:account_id>/<int:page>")
def transactions(account_id, page):
    TRANSACTIONS_PER_PAGE = 20

    account = get_account_or_404(account_id)

    total_transactions_amount = get_count_of_transactions(account_id)
    total_pages = ceil(total_transactions_amount / TRANSACTIONS_PER_PAGE)

    if page < 1 or page > total_pages:
        abort(404, "Page not found")

    has_more = page < total_pages
    print(page, total_pages, has_more)

    account_transactions = get_limited_offset_transactions(account_id, TRANSACTIONS_PER_PAGE, page)

    transactions_list = []

    for transaction in account_transactions:
        transaction_api_model = TransactionsApiModel(transaction)
        transactions_list.append(transaction_api_model)
    transactions_dict = [api_transaction.to_dict() for api_transaction in transactions_list]

    return jsonify({"transactions": transactions_dict, "has_more": has_more})

# TODO HERE make an api for customer profile page

