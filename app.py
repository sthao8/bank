import locale
from babel.numbers import format_currency
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, flash, render_template, request, url_for, redirect
from flask_login import login_required
from flask_mail import Mail
from flask_migrate import Migrate, upgrade
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    RoleMixin,
    UserMixin,
    login_user,
    logout_user,
    roles_required,
    roles_accepted)
from flask_security.utils import hash_password, verify_password
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm

from search_results_handler import SearchResultsHandler

from utils import (
    string_to_bool
    )
from models import (
    User,
    Customer,
    Account,
    Country,
    Transaction,
    Role,
    db)
from seed import (
    seed_countries,
    seed_data,
    seed_roles,
    seed_users
    )
from views.forms import (
    LoginForm,
    RegisterCustomerForm,
    RegisterUserForm,
    CrudUserForm,
    SearchAccountForm,
    SearchCustomerForm,
    TransactionForm,
    TransferForm,
    PrefixedForm
    )
from business_logic.constants import BusinessConstants, AccountTypes, UserRoles, TransactionTypes
from views.authentication import authenticationBluePrint

# TODO let's work on transactions next
# TODO remove confirm old password for admins, maybe keep if there is a user page

locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")

app = Flask(__name__)
app.config.from_object('config.Config')

db.app = app
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(authenticationBluePrint)

mail = Mail(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

app.jinja_env.filters["enumerate"] = enumerate

@app.template_filter()
def format_money(value, currency="SEK"):
    return format_currency(value, currency, locale="sv_SE")

@app.context_processor
def context_processor():
    search_account_form = SearchAccountForm()
    return dict(search_account_form=search_account_form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data).one_or_none()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")

    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@login_required
def index():
    country_stats = db.session.execute(
        select(
            Country.name,
            func.count(func.distinct(Customer.id)).label("number_of_customers"),
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Customer, Customer.country==Country.country_code)
            .join(Account, Account.customer_id==Customer.id)
            .group_by(Customer.country)
            .order_by(desc("sum_of_accounts"))
    ).all()

    global_stats = {
        "number_of_customers": sum([country.number_of_customers for country in country_stats]),
        "number_of_accounts": sum([country.number_of_accounts for country in country_stats]),
        "sum_of_accounts": sum([country.sum_of_accounts for country in country_stats])
    }

    return render_template(
        "index.html",
        active_page="index",
        country_stats=country_stats,
        global_stats=global_stats
    )

@app.route("/search-account-number", methods=["POST"])
@login_required
def search_account_number():
    form = SearchAccountForm()

    if form.validate_on_submit():
        customer = db.session.execute(
            select(Customer)
            .join(Account, Customer.id==Account.id)
            .where(Customer.id==form.search_account_number.data)
        ).one_or_none()

        if customer:
            print(customer)
            return redirect(url_for(
                "customer_page",
                active_page="search_customer", #TODO this is not strictly true
                customer_id=customer.Customer.id,)
            )
        else:
            flash("No results found!")
            return redirect(url_for("search_customer", active_page="search_customer"))
    #TODO actually decide what to do here if they can't validate. maybe front end validation beforehands and then??
    return render_template("404.html")

@app.route("/search-customer")
@login_required
def search_customer():
    form = SearchCustomerForm()

    return render_template(
    "search_customer.html",
    active_page="search_customer",
    form=form)

@app.route("/search-results")
@login_required
def display_search_results():
    form = SearchCustomerForm(request.args)
    handler = SearchResultsHandler(form, request.args, Customer)
    RESULTS_PER_PAGE = 50

    if handler.has_query_criteria:
        customers = handler.get_paginated_sorted_ordered_results(RESULTS_PER_PAGE)

        return render_template(
            "search_results.html",
            active_page="search_customer",
            sort_col=handler.current_sort_col,
            sort_order=handler.sort_order,
            form=form,
            customers=customers,
            page=handler.page)
    else:
        return render_template(
            "search_results.html",
            active_page="search_customer",
            form=form,
            customers=None)

@app.route("/country-page/<country>", methods=["GET"])
@login_required
def country_page(country):
    countries = db.session.execute(select(Country.name)).scalars().all()
    
    if country in countries:
        country_customers = db.session.execute(
            select(
            Customer, 
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Account, Account.customer_id==Customer.id)
            .join(Country, Country.country_code==Customer.country)
            .where(Country.name==country)
            .group_by(Customer.id)
            .order_by(desc("sum_of_accounts"))
            .limit(10)
        ).all()

        return render_template(
            "country_page.html",
            active_page="index",
            country=country,
            country_customers=country_customers)
    
    else:
        return render_template("404.html")

@app.route("/customer/<customer_id>", methods=["GET"])
@login_required
def customer_page(customer_id):
    customer = Customer.query.filter_by(id=customer_id).options(
        joinedload(Customer.accounts),
        joinedload(Customer.country_details)
    ).one_or_none()
    
    if customer:
        total_balance = sum([account.balance for account in customer.accounts])
        return render_template(
            "customer_page.html",
            customer=customer,
            total_balance=total_balance)
    else:
        return render_template("404.html")
    
@app.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
    #TODO Like ajax fetch this in html OR something
    account = Account.query.filter_by(id=account_id).one_or_none()
    if account:
        transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).all()
        print(transactions)
        return render_template("account_page.html", account=account, transactions=transactions)
    else:
        return render_template("404.html")

@app.route("/register_customer", methods=["GET", "POST"])
@login_required
def register_customer():
    # TODO: do maybe some more validation stuff here

    countries = Country.query.all()
    form = RegisterCustomerForm()
    form.register_country.choices = [(country.country_code, country.name) for country in countries]

    if form.validate_on_submit():
        new_customer = Customer()

        for field_name, field in form._fields.items():
            if field_name.startswith(form.field_prefix):
                model_col_name = form.get_column_name(field_name)
                setattr(new_customer, model_col_name, field.data)

        new_account = Account()
        new_account.account_type = AccountTypes.CHECKING.value
        new_account.created = datetime.now()
        new_account.balance = 0 # TODO: not sure about this. maybe all accounts should start with 0?
        new_customer.accounts.append(new_account)

        db.session.add(new_customer)
        db.session.add(new_account)
        db.session.commit()

        flash("Successfully added customer")
        return redirect(url_for("customer_page", customer_id=new_customer.id))

    return render_template(
        "register_customer.html",
        form=form,
        active_page="register_customer")

@app.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def crud_user():
    user_roles = [role.value for role in UserRoles]

    crud_form = CrudUserForm()
    crud_form.crud_role.choices = user_roles

    register_form = RegisterUserForm()
    register_form.register_role.choices = user_roles

    current_users  = User.query.filter_by(active=True).all()

    return render_template("users.html", active_page="crud_user", crud_form=crud_form, register_form=register_form, current_users=current_users)

@app.route("/register_user", methods=["POST"])
@roles_accepted("admin")
def register_user():
    form: FlaskForm = RegisterUserForm()
    form.register_role.choices = [role.value for role in UserRoles]

    if form.validate_on_submit():
        user_datastore.create_user(
            email=form.register_email.data,
            password=hash_password(form.register_password.data),
            active=True,
            roles=[form.register_role.data])
        
        db.session.commit()
        flash("user registered")
    else:
        flash("didn't pass validation")
    return redirect(url_for("crud_user"))

@app.route("/update_user", methods=["POST"])
@roles_accepted("admin")
def update_user():
    form = CrudUserForm()
    form.crud_role.choices = [role.value for role in UserRoles]

    user_id = request.form.get("user_id", None, int)
    user = user_datastore.find_user(id=user_id)

    if user and form.validate_on_submit():
        new_role = form.crud_role.data
        new_password = form.crud_new_password.data
        if new_password:
            if not verify_password(form.crud_old_password.data, user.password):
                flash("Invalid password")
            else:
                if verify_password(new_password, user.password):
                    flash("password cannot be the same as old password")
                else:
                    user.password = hash_password(new_password)
                    flash("password changed")
        if new_role not in user.roles:
            user_datastore.remove_role_from_user(user, user.roles[0])
            user_datastore.add_role_to_user(user, new_role)
            flash(f"role {new_role} added")
        db.session.commit()
    else:
        flash("didn't pass validation")
    return redirect(url_for("crud_user"))

@app.route("/delete_user", methods=["POST"])
@roles_accepted("admin")
def delete_user():
    user_id = request.form.get("user_id", None, int)
    user = user_datastore.find_user(id=user_id)

    if user:
        user_datastore.deactivate_user(user)
        db.session.commit()
        flash("user deleted")
    else:
        flash("no such user")
    return redirect(url_for("crud_user"))

@app.route("/transactions", methods=["POST"])
@roles_accepted("cashier")
def transactions():
    customer_id = request.form.get("customer_id", None)
    customer = Customer.query.filter_by(id=customer_id).options(joinedload(Customer.accounts)).one_or_none()
    if customer:
        form: PrefixedForm = TransactionForm()
        form.trans_type.choices = ["withdraw", "deposit"]
        accounts_labels = [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
        form.trans_accounts.choices = accounts_labels
        current_date = date.today()

        return render_template("transactions.html", active_page="transaction", form=form, current_date=current_date, customer=customer)
    else:
        flash("no such customer")
        return redirect(url_for("index"))

@app.route("/transfer", methods=["POST"])
@roles_accepted("cashier")
def transfer():
    customer_id = request.form.get("customer_id", None)
    customer = Customer.query.filter_by(id=customer_id).options(joinedload(Customer.accounts)).one_or_none()
    if customer:
        form = TransferForm()
        current_date = date.today()

        return render_template(active_page="transfer", form=form, current_date=current_date)
    else:
        flash("no such customer")
        return redirect(url_for("index"))
    
@app.route("/process-transaction", methods=["POST"])
@roles_accepted("cashier")
def process_transaction():
    customer_id = request.form.get("customer_id", None)
    customer = Customer.query.filter_by(id=customer_id).options(joinedload(Customer.accounts)).one_or_none()
    
    form = TransactionForm()
    form: PrefixedForm = TransactionForm()
    form.trans_type.choices = ["withdraw", "deposit"]
    accounts_labels = [(account.id, f"{account.id}: current balance: {format_money(account.balance)}") for account in customer.accounts]
    form.trans_accounts.choices = accounts_labels

    account: Account = Account.query.filter_by(id=int(form.trans_accounts.data)).one_or_none()
    
    if customer and account and form.validate_on_submit():

        amount = form.trans_amount.data
        if form.trans_type.data == "withdraw":
            transaction_type = TransactionTypes.CREDIT.value
            if amount > account.balance:
                flash("Cannot withdraw more than account balance")
                return redirect(url_for("customer_page", customer_id=customer.id))
        elif form.trans_type.data == "deposit":
            transaction_type = TransactionTypes.DEBIT.value

        transaction = Transaction()
        transaction.amount = amount
        transaction.type = transaction_type
        transaction.timestamp = datetime.now()
        # TODO need to test this some more. math not working out right
        transaction.new_balance = account.balance + amount if transaction_type == "deposit" else account.balance - amount
        transaction.account_id = account.id

        db.session.add(transaction)
        db.session.commit()
        flash(f"success! {transaction.type} money in account number {account.id}.")
        return redirect(url_for("customer_page", customer_id=customer.id))
    flash("didn't pass validation")
    return redirect(url_for("customer_page"), customer_id=customer.id)

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seed_countries(db)
        seed_data(db)
        seed_roles(db, user_datastore)
        seed_users(db, user_datastore)
    
    app.run(debug=True)
