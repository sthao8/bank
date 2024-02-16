from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_security import roles_accepted, roles_required
from flask_security.utils import verify_password, hash_password
from models import user_datastore, db
from views.forms import CrudUserForm, RegisterUserForm, FlaskForm

from utils import string_to_bool
from .services import (
    get_user_roles,
    get_all_users,
    create_and_register_user,
    update_password,
    update_role,
    get_user)

users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def crud_user():
    show_inactive_users = "show_inactive_users" in request.args

    user_roles = get_user_roles()

    crud_form = CrudUserForm()
    crud_form.crud_role.choices = user_roles

    register_form = RegisterUserForm()
    register_form.register_role.choices = user_roles

    users  = get_all_users()
    if not show_inactive_users:
        users = [user for user in users if user.active]

    return render_template(
        "users/users.html",
        active_page="crud_user",
        show_inactive_users=show_inactive_users,
        crud_form=crud_form,
        register_form=register_form,
        users=users)

@users_blueprint.route("/user-page/<user_id>", methods=["GET"])
@roles_required("admin")
def user_page(user_id):
    user = get_user(user_id)

    form = CrudUserForm()
    form.crud_role.choices = get_user_roles()
    form.crud_role.data = user.roles[0]
    return render_template("users/edit_user.html", user=user, form=form)


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
        changes_made = False

        if new_password:
            if verify_password(new_password, user.password):
                flash("password cannot be the same as old password")
            else:
                update_password(user, new_password)
                flash("password changed")
                changes_made = True
        if new_role not in user.roles:
            update_role(user, new_role)
            flash(f"role {new_role} added")
            changes_made = True
        if changes_made:
            db.session.commit()
        else:
            flash("No changes made!")
    else:
        flash("didn't pass validation")
    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/change_user_status", methods=["POST"])
@roles_accepted("admin")
def change_user_status():
    user_id = request.form.get("user_id", None, int)
    user = user_datastore.find_user(id=user_id)

    if user:
        if user.active:
            user_datastore.deactivate_user(user)
            message = "user deactivated"
        else:
            user_datastore.activate_user(user)
            message = "user activated"
        db.session.commit()
        flash(message)
        return redirect(url_for("users.user_page", user_id=user.id))
    else:
        flash("no such user")
    return redirect(url_for("users.crud_user"))
