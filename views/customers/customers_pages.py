from flask import Blueprint, render_template, redirect, flash, url_for
from flask_security import login_required

from models import db
from .services import (
    get_customer_from_id,
    get_account_from_id,
    get_transactions_from_account_id,
    get_all_countries,
    create_customer_and_new_account,
    get_country_stats,
    get_supported_country_names,
    get_country_customer
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
    supported_countries = get_supported_country_names()
    
    if country in supported_countries:
        country_customer = get_country_customer(country)
        
        return render_template(
            "customers/country_page.html",
            active_page="index",
            country=country,
            country_customers=country_customer)
    
    else:
        return render_template("404.html")

    
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
    customer = get_customer_from_id(customer_id)
    
    if customer:
        total_balance = sum([account.balance for account in customer.accounts])
        return render_template(
            "customers/customer_page.html",
            customer=customer,
            total_balance=total_balance)

@customers_blueprint.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
    #TODO Like ajax fetch this in html OR something
    account = get_account_from_id(account_id)
    if account:
        transactions = get_transactions_from_account_id(account_id)
        return render_template("customers/account_page.html", account=account, transactions=transactions)
