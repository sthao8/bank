from flask import Flask, flash, render_template, request, session, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from models import (
    User,
    Customer,
    Account,
    Country,
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
    country_stmt = (select(
            Country.name,
            func.count(func.distinct(Customer.id)).label("number_of_customers"),
            func.count(Account.id).label("number_of_accounts"),
            func.sum(Account.balance).label("sum_of_accounts"))
            .join(Customer, Customer.country==Country.country_code)
            .join(Account, Account.customer_id==Customer.id)
            .group_by(Customer.country)
            .order_by("sum_of_accounts")
    )
    country_stats = [
        {
            "country": name,
            "number_of_customers": number_of_customers,
            "number_of_accounts": number_of_accounts,
            "sum_of_accounts": sum_of_accounts
        }
        for (name, number_of_customers, number_of_accounts, sum_of_accounts) in db.session.execute(country_stmt).all()
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

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seed_countries(db)
        seed_data(db)
        seed_users(db)
    
    app.run(debug=True)
