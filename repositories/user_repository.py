from models import User, user_datastore, db
from sqlalchemy import desc
from business_logic.constants import UserRoles
from flask_security.utils import verify_password, hash_password

class UserRepository():
    def get_user_from_email(user_email):
        return User.query.filter_by(email=user_email).one_or_none()

    def get_user_from_id(user_id):
        return user_datastore.find_user(id=user_id)

    def get_user_or_404(user_id):
        return User.query.filter_by(id=user_id).one_or_404()

    def get_all_users():
        return User.query.order_by(desc(User.active)).all()
    
    def get_active_users():
        return User.query.filter_by(active=True).all()
    
    def get_user_roles():
        return [role.value for role in UserRoles]

    def create_and_register_user(form) -> None:
        user_datastore.create_user(
                email=form.email.data,
                password=hash_password(form.password.data),
                active=True,
                roles=[form.role.data])
        db.session.commit()
    
    def update_password(user, new_password):
        user.password = hash_password(new_password)
        db.session.commit()
    
    def update_role(user, new_role):
        user_datastore.remove_role_from_user(user, user.role)
        user_datastore.add_role_to_user(user, new_role)
        db.session.commit()

    def deactivate_user(user):
        user_datastore.deactivate_user(user)
        db.session.commit()
    
    def activate_user(user):
        user_datastore.activate_user(user)
        db.session.commit()

    def delete_user(user):
        user.email = None
        user.password = None
        user.active = False
        user.roles = []
        db.session.commit()