from flask_login import login_user, login_required, logout_user
from flask import redirect, url_for, flash, render_template, Blueprint

from views.forms import LoginForm
from services.user_services import UserService, UserRepository


user_service = UserService(UserRepository)

authentication_blueprint = Blueprint("authentication", __name__)

@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = user_service.authenticate_user(form.email.data, form.password.data)
        except ValueError as error:
            flash(f"ERROR: {error}")
        else:
            login_user(user)
            return redirect(url_for("customers.index"))

    return render_template("authentication/login.html", form=form)

@authentication_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))
