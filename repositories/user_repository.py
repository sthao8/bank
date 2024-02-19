from models import User, user_datastore, UserRoles
from flask_security.utils import verify_password, hash_password

class UserRepository():
    def get_user_from_email(user_email):
        return User.query.filter_by(email=user_email).one_or_none()

    def get_user_from_id(user_id):
        return User.query.filter_by(id=user_id).one_or_404()

    def get_all_users():
        return User.query.all()
    
    def get_user_roles():
        return [role.value for role in UserRoles]

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