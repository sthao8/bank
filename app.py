import locale
from flask import Flask
from extenstions import mail
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
from views.authentication_pages import authentication_blueprint
from views.users_pages import users_blueprint
from views.customers_pages import customers_blueprint
from views.search_pages import search_blueprint
from views.transactions_pages import transactions_blueprint


# TODO maybe simplify my prefixed forms
# TODO work on frontend errors

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

    security = Security(app, user_datastore)

    app.jinja_env.filters["enumerate"] = enumerate

    mail.init_app(app)

    app.template_filter("format_money")(format_money)

    @app.context_processor
    def context_processor():
        search_account_form = SearchAccountForm()
        return dict(search_account_form=search_account_form)
    
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
