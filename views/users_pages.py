from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_security import roles_accepted, roles_required
from flask_security.utils import verify_password, hash_password
from models import user_datastore, db
from views.forms import CrudUserForm, RegisterUserForm, FlaskForm

from utils import string_to_bool
from repositories.user_repository import UserRepository
from services.user_services import UserService


user_service = UserService(UserRepository)

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def crud_user():
    show_inactive_users = "show_inactive_users" in request.args

    user_roles = user_service.get_user_roles()

    crud_form = CrudUserForm()
    crud_form.crud_role.choices = user_roles

    register_form = RegisterUserForm()
    register_form.register_role.choices = user_roles

    users  = user_service.fetch_users_by_active_status(show_inactive_users)

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
    user = user_service.get_user_or_404(user_id)

    form = CrudUserForm()
    form.crud_role.choices = user_service.get_user_roles()
    form.crud_role.data = user.roles[0]

    return render_template("users/edit_user.html", user=user, form=form)


@users_blueprint.route("/register_user", methods=["POST"])
@roles_accepted("admin")
def register_user():
    form: FlaskForm = RegisterUserForm()
    form.register_role.choices = user_service.get_user_roles()

    if form.validate_on_submit():
        try:
            user_service.create_and_register_user(form)
            flash("User registered")
        except ValueError as error:
            flash(f"ERROR: {error}")
    else:
        flash("Didn't pass validation")

    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/update_user", methods=["POST"])
@roles_accepted("admin")
def update_user():
    form = CrudUserForm()
    form.crud_role.choices = user_service.get_user_roles()

    user_id = request.form.get("user_id", None, int)
    user = user_service.get_user_or_404(user_id)

    if form.validate_on_submit():
        new_role = form.crud_role.data
        new_password = form.crud_new_password.data
        
        try:
            if user_service.update_user_if_changes(user, new_password, new_role):
                flash("User updated")
            else:
                flash("No changes made!")
        except ValueError as error:
            flash(f"Error: {error}")
    else:
        flash("didn't pass validation")
    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/change_user_status", methods=["POST"])
@roles_accepted("admin")
def change_user_status():
    user_id = request.form.get("user_id", None, int)
    user = user_service.get_user_or_404(user_id)

    result = user_service.changed_user_status(user)
    flash(result)
    
    return redirect(url_for("users.user_page", user_id=user.id))
