from flask import Flask, flash, render_template, request, session, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func, desc
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
from views.forms import LoginForm


app = Flask(__name__)
app.config.from_object('config.Config')

db.app = app
db.init_app(app)
migrate = Migrate(app, db)

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
    country_results = db.session.execute(
        select(
            Country.name,
            func.count(func.distinct(Customer.id)).label("number_of_customers"),
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Customer, Customer.country==Country.country_code)
            .join(Account, Account.customer_id==Customer.id)
            .group_by(Customer.country)
            .order_by("sum_of_accounts")
    ).all()

    country_stats = [
        {
            "country": name,
            "number_of_customers": number_of_customers,
            "number_of_accounts": number_of_accounts,
            "sum_of_accounts": sum_of_accounts
        }
        for (name, number_of_customers, number_of_accounts, sum_of_accounts) in country_results
    ]

    global_stats = {
        "number_of_customers": sum([country["number_of_customers"] for country in country_stats]),
        "number_of_accounts": sum([country["number_of_accounts"] for country in country_stats]),
        "sum_of_accounts": sum([country["sum_of_accounts"] for country in country_stats])
    }

    return render_template(
        "index.html",
        country_stats=country_stats,
        global_stats=global_stats
    )

@app.route("/country-page/<country>", methods=["GET"])
@login_required
def country_page(country):
    countries = db.session.execute(select(Country.name)).scalars().all()
    
    if country in countries:
        country_customers_results = db.session.execute(
            select(
            Customer, 
            func.count(Account.id),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Account, Account.customer_id==Customer.id)
            .join(Country, Country.country_code==Customer.country)
            .where(Country.name==country)
            .group_by(Customer.id)
            .order_by(desc("sum_of_accounts"))
            .limit(10)
        ).all()

        country_customers = [
            {
            "customer": customer,
            "number_of_accounts": number_of_accounts,
            "sum_of_accounts": sum_of_accounts}
            for (customer, number_of_accounts, sum_of_accounts) in country_customers_results
        ]

        return render_template(
        "country_page.html",
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
        return render_template("customer_page.html", customer=customer, total_balance=total_balance)
    else:
        return render_template("404.html")
    
@app.route("/account/<account_id>", methods=["GET"])
@login_required
def account_page(account_id):
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
