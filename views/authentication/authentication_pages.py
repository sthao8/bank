from flask_login import login_user, login_required, logout_user
from flask import redirect, url_for, flash, render_template, Blueprint
from flask_security.utils import hash_password, verify_password


from .services import get_user_from_email
from views.forms import LoginForm

authentication_blueprint = Blueprint("authentication", __name__)

@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = get_user_from_email(form.email.data)

        if user and verify_password(form.password.data, user.password):
            login_user(user)
            return redirect(url_for("customers.index"))
        else:
            flash("Invalid username or password")

    return render_template("authentication/login.html", form=form)

@authentication_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))
