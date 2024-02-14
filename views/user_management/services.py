from models import UserRoles, User, db, user_datastore
from flask_security.utils import verify_password, hash_password


def get_user_roles():
    return [role.value for role in UserRoles]

def get_current_users():
    return User.query.filter_by(active=True).all()

def create_and_register_user(form) -> None:
    user_datastore.create_user(
            email=form.register_email.data,
            password=hash_password(form.register_password.data),
            active=True,
            roles=[form.register_role.data])

def update_password(user, new_password):
    user.password = hash_password(new_password)

def update_role(user, new_role):
    user_datastore.remove_role_from_user(user, user.roles[0])
    user_datastore.add_role_to_user(user, new_role)
