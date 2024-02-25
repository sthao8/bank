from repositories.user_repository import UserRepository
from flask_security.utils import verify_password, hash_password
from flask_login import login_user, logout_user
from models import user_datastore, User

class UserService():
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
    
    def get_all_users(self):
        return self.user_repository.get_all_users()
    
    def fetch_users_by_active_status(self, show_inactive_users):
        return self.user_repository.get_all_users() if show_inactive_users else self.user_repository.get_active_users()
    
    def get_user_roles(self):
        return self.user_repository.get_user_roles()
    
    def get_user_from_email(self, email):
        return self.user_repository.get_user_from_email(email)

    def get_user_from_id(self, user_id):
        return self.user_repository.get_user_from_id(user_id)
    
    def get_user_or_404(self, user_id):
        return self.user_repository.get_user_or_404(user_id)
    
    def create_and_register_user(self, form):
        email = form.register_email.data
        user = self.user_repository.get_user_from_email(email)
        if not user:
            return self.user_repository.create_and_register_user(form)
        else:
            raise ValueError(f"User with email {email} already exists.")
    
    def update_user_if_changes(self, user, new_password, new_role) -> bool:
        changes_made = False
        if new_password:
            if verify_password(new_password, user.password):
                raise ValueError("password cannot be the same as old password")
            else:
                self.user_repository.update_password(user, new_password)
                changes_made = True
        if new_role not in user.roles:
            self.user_repository.update_role(user, new_role)
            changes_made = True
        return changes_made
    
    def changed_user_status(self, user) -> str:
        if user.active:
            self.user_repository.deactivate_user(user)
            message = "user deactivated"
        else:
            self.user_repository.activate_user(user)
            message = "user activated"
        return message
    
    def deleted_user(self, user) -> str:
        return self.user_repository.delete_user(user)

    def authenticate_user(self, email, password) -> User:
        user = user_datastore.find_user(email=email)

        if user and verify_password(password, user.password):
            return user
        else:
            raise ValueError("Invalid username or password")