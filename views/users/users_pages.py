from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_security import roles_accepted, roles_required
from flask_security.utils import verify_password, hash_password
from models import user_datastore, db
from views.forms import CrudUserForm, RegisterUserForm, FlaskForm

from .services import get_user_roles, get_current_users, create_and_register_user, update_password, update_role

users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def crud_user():
    user_roles = get_user_roles()

    crud_form = CrudUserForm()
    crud_form.crud_role.choices = user_roles

    register_form = RegisterUserForm()
    register_form.register_role.choices = user_roles

    current_users  = get_current_users()

    return render_template("users/users.html", active_page="crud_user", crud_form=crud_form, register_form=register_form, current_users=current_users)

@users_blueprint.route("/register_user", methods=["POST"])
@roles_accepted("admin")
def register_user():
    form: FlaskForm = RegisterUserForm()
    form.register_role.choices = get_user_roles()

    if form.validate_on_submit():
        create_and_register_user(form)
        db.session.commit()
        flash("user registered")
    else:
        flash("didn't pass validation")
    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/update_user", methods=["POST"])
@roles_accepted("admin")
def update_user():
    form = CrudUserForm()
    form.crud_role.choices = get_user_roles()

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
                    update_password(user, new_password)
                    flash("password changed")
        if new_role not in user.roles:
            update_role(user, new_role)
            flash(f"role {new_role} added")
        db.session.commit()
    else:
        flash("didn't pass validation")
    return redirect(url_for("users.crud_user"))


@users_blueprint.route("/delete_user", methods=["POST"])
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
    return redirect(url_for("users.crud_user"))