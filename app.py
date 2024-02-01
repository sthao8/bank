from flask import Flask, flash, render_template, request, session, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import joinedload

from models import (
    User,
    Customer,
    Account,
    Country,
    Transaction,
    db,
    seed_countries,
    seed_data,
    seed_users
)
from views.forms import LoginForm, SearchAccountForm, SearchCustomerForm


app = Flask(__name__)
app.config.from_object('config.Config')

db.app = app
db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def context_processor():
    search_account_form = SearchAccountForm()
    return dict(search_account_form=search_account_form)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        activePage="index",
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
                activePage="search_customer", #TODO this is not strictly true
                customer_id=customer.Customer.id,)
            )
        else:
            flash("No results found!")
            return redirect(url_for("search_customer", activePage="search_customer"))
    #TODO actually decide what to do here if they can't validate. maybe front end validation beforehands and then??
    return render_template("404.html")

@app.route("/search-customer")
@login_required
def search_customer():
    form = SearchCustomerForm()

    return render_template(
    "search_customer.html",
    activePage="search_customer",
    form=form)

@app.route("/search-results")
@login_required
def display_search_results():
    form = SearchCustomerForm(request.args) #needed bc it's a get

    if form.validate():
        sort_col = request.args.get("sort_col", "id")
        sort_order = request.args.get("sort_order", "asc")

        sort_critera = getattr(Customer, sort_col) # gets the attr from string

        if sort_order == "asc":
            stmt = Customer.query.filter(
                func.lower(Customer.first_name)==form.search_first_name.data.lower(),
                func.lower(Customer.last_name)==form.search_last_name.data.lower(),
                func.lower(Customer.city)==form.search_city.data.lower()
            ).order_by(asc(sort_critera))
            customers = Customer.query.filter(
                func.lower(Customer.first_name)==form.search_first_name.data.lower(),
                func.lower(Customer.last_name)==form.search_last_name.data.lower(),
                func.lower(Customer.city)==form.search_city.data.lower()
            ).order_by(asc(sort_critera)).all()
        else:
            stmt = customers = Customer.query.filter(
                func.lower(Customer.first_name)==form.search_first_name.data.lower(),
                func.lower(Customer.last_name)==form.search_last_name.data.lower(),
                func.lower(Customer.city)==form.search_city.data.lower()
            ).order_by(desc(sort_critera))
            customers = Customer.query.filter(
                func.lower(Customer.first_name)==form.search_first_name.data.lower(),
                func.lower(Customer.last_name)==form.search_last_name.data.lower(),
                func.lower(Customer.city)==form.search_city.data.lower()
            ).order_by(desc(sort_critera)).all()

        print(stmt) 

        return render_template(
            "search_results.html",
            activePage="search_customer",
            sort_col=sort_col,
            sort_order=sort_order,
            form=form,
            customers=customers)

    else:
        #TODO maybe something else?
        # return redirect(url_for("search_customer"))
        return render_template('404.html')

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
            activePage="index",
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


if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seed_countries(db)
        seed_data(db)
        seed_users(db)
    
    app.run(debug=True)
