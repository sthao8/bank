from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_security import roles_accepted, roles_required
from forms import CrudUserForm, RegisterUserForm, FlaskForm

from repositories.user_repository import UserRepository
from services.user_services import UserService

from utils import get_first_error_message


user_repo = UserRepository()
user_service = UserService(user_repo)

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def crud_user():
    show_inactive_users = "show_inactive_users" in request.args

    user_roles = user_service.get_user_roles()

    crud_form = CrudUserForm()
    crud_form.role.choices = user_roles

    register_form = RegisterUserForm()
    register_form.role.choices = user_roles

    users  = user_service.fetch_users_by_active_status(show_inactive_users)

    return render_template(
        "users/users.html",
        active_page="crud_user",
        show_inactive_users=show_inactive_users,
        crud_form=crud_form,
        register_form=register_form,
        users=users)

@users_blueprint.route("/register_user", methods=["POST"])
@roles_accepted("admin")
def register_user():
    form: FlaskForm = RegisterUserForm()
    form.role.choices = user_service.get_user_roles()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        role = form.role.data
        try:
            user_service.create_and_register_user(email, password, role)
            flash("User registered")
        except ValueError as error:
            flash(f"ERROR: {error}")
    else:
        flash(f"ERROR: {get_first_error_message(form.errors)}")

    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/update_user", methods=["POST"])
@roles_accepted("admin")
def update_user():
    form = CrudUserForm()
    form.role.choices = user_service.get_user_roles()

    user_id = request.form.get("user_id", None, int)
    user = user_service.get_user_or_404(user_id)

    if form.validate_on_submit():
        new_role = form.role.data
        new_password = form.new_password.data
        
        try:
            if user_service.update_user(user, new_password, new_role):
                flash("User updated")
            else:
                flash("No changes made!")
        except ValueError as error:
            flash(f"Error: {error}")
    else:
        flash(f"ERROR: {get_first_error_message(form.errors)}")
    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/change_user_status", methods=["POST"])
@roles_accepted("admin")
def change_user_status():
    user_id = request.form.get("user_id", None, int)
    user = user_service.get_user_or_404(user_id)

    result = user_service.change_user_status(user)
    flash(result)
    
    return redirect(url_for("users.crud_user"))

@users_blueprint.route("/delete_user", methods=["POST"])
@roles_accepted("admin")
def delete_user():
    user_id = request.form.get("user_id", None, int)
    user = user_service.get_user_or_404(user_id)

    user_service.delete_user(user)
    flash("User deleted")
    
    return redirect(url_for("users.crud_user"))
