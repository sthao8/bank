from models import User, user_datastore, db, Role
from sqlalchemy import desc
from constants.constants import UserRoles
from flask_security.utils import verify_password, hash_password

class UserRepository():
    def get_user_from_email(self, user_email: str) -> User:
        return User.query.filter_by(email=user_email).one_or_none()

    def get_user_or_404(self, user_id) -> User:
        return User.query.filter_by(id=user_id).one_or_404()

    def get_all_users(self) -> list[User]:
        return User.query.order_by(desc(User.active)).all()
    
    def get_active_users(self) -> list[User]:
        return User.query.filter_by(active=True).all()

    def create_and_register_user(self, email: str, password: str, role: str) -> None:
        user_datastore.create_user(
                email=email,
                password=hash_password(password),
                active=True,
                roles=[role])
        db.session.commit()
    
    def update_password(self, user: User, new_password: str) -> None:
        user.password = hash_password(new_password)
        db.session.commit()
    
    def update_role(self, user: User, new_role: Role|str) -> None:
        user_datastore.remove_role_from_user(user, user.roles[0])
        user_datastore.add_role_to_user(user, new_role)
        db.session.commit()

    def deactivate_user(self, user: User) -> None:
        user_datastore.deactivate_user(user)
        db.session.commit()
    
    def activate_user(self, user: User) -> None:
        user_datastore.activate_user(user)
        db.session.commit()

    def delete_user(self, user: User) -> None:
        user.email = None
        user.password = None
        user.active = False
        user.roles = []
        db.session.commit()