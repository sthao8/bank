from flask import Blueprint, render_template, redirect, flash, url_for
from flask_security import login_required, roles_accepted

from forms import RegisterCustomerForm

from services.country_services import CountryService, CountryRepository
from services.transaction_services import TransactionService, TransactionRepository
from services.customer_services import CustomerService, CustomerRepository
from services.account_services import AccountService, AccountRepository


customers_blueprint = Blueprint("customers", __name__)

country_repo = CountryRepository()
country_service = CountryService(country_repo)

account_repo = AccountRepository()
account_service = AccountService(account_repo)

customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo, account_service)

transaction_repo = TransactionRepository()
transaction_service = TransactionService(transaction_repo, account_service)

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

    country_customer = customer_service.get_top_10_customers_for_country(country.name)
    
    return render_template(
        "customers/country_page.html",
        active_page="index",
        country=country.name,
        country_customers=country_customer)
    
@customers_blueprint.route("/register_customer", methods=["GET", "POST"])
@roles_accepted("cashier", "admin")
def register_customer():
    form = RegisterCustomerForm()
    form.country.choices = country_service.get_form_country_choices()

    if form.validate_on_submit():
        customer_details = {
            fieldname: field.data for fieldname, field in form._fields.items()
            if fieldname in form.user_defined_fields
            }

        try:
            new_customer = customer_service.create_customer_and_new_account(customer_details)
        except ValueError as error:
            flash(f"ERROR: {error}")
        else:
            flash("Successfully added customer")
            return redirect(url_for("customers.customer_page", customer_id=new_customer.id))

    return render_template(
        "customers/customer_details.html",
        form=form,
        active_page="register_customer",
        edit=False)

@customers_blueprint.route("/customer/<customer_id>", methods=["GET"])
@login_required
def customer_page(customer_id):
    customer = customer_service.get_customer_accounts_country(customer_id)
    
    total_balance = sum([account.balance for account in customer.accounts])

    return render_template(
        "customers/customer_page.html",
        customer=customer,
        total_balance=total_balance
        )

@customers_blueprint.route("/edit-customer/<int:customer_id>")
@roles_accepted("cashier", "admin")
def edit_customer(customer_id):
    customer = customer_service.get_customer_accounts_country(customer_id)

    form = RegisterCustomerForm(obj=customer)
    form.country.choices = country_service.get_form_country_choices()

    return render_template("customers/customer_details.html", customer=customer, form=form, edit=True)

@customers_blueprint.route("/process-customer-edits", methods=["POST"])
@roles_accepted("cashier", "admin")
def process_customer_edits():
    form = RegisterCustomerForm()
    form.country.choices = country_service.get_form_country_choices()
    
    customer = customer_service.get_customer_from_national_id(form.national_id.data)

    if form.validate_on_submit() and customer:
        customer_details = {
            fieldname: field.data for fieldname, field in form._fields.items()
            if fieldname in form.user_defined_fields}

        if customer_service.customer_edited(customer, customer_details):
            flash("Customer details updated!")
        else:
            flash("No changes to customer made!")
    else:
        flash("Errors updating customer.")
    return redirect(url_for("customers.customer_page", customer_id=customer.id))

@customers_blueprint.route("/account/<account_id>", methods=["GET"])
@roles_accepted("cashier", "admin")
def account_page(account_id):
    account = account_service.get_account_from_id(account_id, raise_404=True)
    return render_template("customers/account_page.html", account=account)
