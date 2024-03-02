import locale
from flask import Flask
from extensions import mail
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
from forms import SearchCustomerIDForm
from views.authentication_pages import authentication_blueprint
from views.users_pages import users_blueprint
from views.customers_pages import customers_blueprint
from views.search_pages import search_blueprint
from views.transactions_pages import transactions_blueprint
from views.api import api_blueprint


def create_app():
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
    app.register_blueprint(api_blueprint)

    security = Security(app, user_datastore)

    app.jinja_env.filters["enumerate"] = enumerate

    mail.init_app(app)

    app.template_filter("format_money")(format_money)

    @app.context_processor
    def inject_search_account_form():
        search_account_form = SearchCustomerIDForm()
        return dict(search_account_form=search_account_form)
    
    @app.context_processor
    def inject_validation_failed():
        """Return this when serverside validation fails to next route
        in order to reset validation of empty fields, like password"""
        return dict(validation_failed=False)
        
    return app


if __name__  == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()
        seed_countries(db)
        seed_data(db)
        seed_roles(db, user_datastore)
        seed_users(db, user_datastore)
    
    app.run(debug=True)
