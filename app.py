import locale
from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate, upgrade
from flask_security import Security

from utils import format_money
from models import db, user_datastore
from seed import (
    seed_countries,
    seed_data,
    seed_roles,
    seed_users
    )
from views.forms import SearchAccountForm
from views.authentication.authentication_pages import authentication_blueprint
from views.users.users_pages import users_blueprint
from views.customers.customers_pages import customers_blueprint
from views.search.search_pages import search_blueprint
from views.transactions.transactions_pages import transactions_blueprint

# TODO FIX so that in crud users, deactivate/activate + populate each with old role
# TODO maybe simplify my prefixed forms


locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")

app = Flask(__name__)
app.config.from_object('config.Config')

db.app = app
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(authentication_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(customers_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(transactions_blueprint)

mail = Mail(app)

security = Security(app, user_datastore)

app.jinja_env.filters["enumerate"] = enumerate

app.template_filter("format_money")(format_money)

@app.context_processor
def context_processor():
    search_account_form = SearchAccountForm()
    return dict(search_account_form=search_account_form)

if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seed_countries(db)
        seed_data(db)
        seed_roles(db, user_datastore)
        seed_users(db, user_datastore)
    
    app.run(debug=True)
