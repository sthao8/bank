from flask import Blueprint, render_template, redirect, flash, url_for
from flask_security import login_required

from models import db
from .services import get_customer_from_id, get_account_from_id, get_transactions_from_account_id, get_all_countries, create_customer
from views.forms import RegisterCustomerForm

customer_management_blueprint = Blueprint("customer_management", __name__)


@customer_management_blueprint.route("/customer/<customer_id>", methods=["GET"])
@login_required
def customer_page(customer_id):
    customer = get_customer_from_id(customer_id)
    
    if customer:
        total_balance = sum([account.balance for account in customer.accounts])
        return render_template(
            "customer_management/customer_page.html",
            customer=customer,
            total_balance=total_balance)

@customer_management_blueprint.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
    #TODO Like ajax fetch this in html OR something
    account = get_account_from_id(account_id)
    if account:
        transactions = get_transactions_from_account_id(account_id)
        return render_template("customer_management/account_page.html", account=account, transactions=transactions)
    
@customer_management_blueprint.route("/register_customer", methods=["GET", "POST"])
@login_required
def register_customer():
    # TODO: do maybe some more validation stuff here

    countries = get_all_countries()
    form = RegisterCustomerForm()
    form.register_country.choices = [(country.country_code, country.name) for country in countries]

    if form.validate_on_submit():
        new_customer = create_customer(form)
        db.session.add(new_customer)
        db.session.commit()

        flash("Successfully added customer")
        return redirect(url_for("customer_management.customer_page", customer_id=new_customer.id))

    return render_template(
        "customer_management/register_customer.html",
        form=form,
        active_page="register_customer")
