from flask_login import login_user, login_required, logout_user
from flask import redirect, url_for, flash, render_template, Blueprint

from .services import get_user
from forms import LoginForm

authenticationBluePrint = Blueprint("authentication", __name__)

@authenticationBluePrint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = get_user(form.email.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")

    return render_template("login.html", form=form)

@authenticationBluePrint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
