from repositories.user_repository import UserRepository
from flask_security.utils import verify_password
from models import user_datastore, User, Role
from constants.constants import UserRoles
from constants.errors_messages import ErrorMessages

class UserService():
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
    
    def get_all_users(self):
        return self.user_repository.get_all_users()
    
    def fetch_users_by_active_status(self, show_inactive_users):
        return (self.user_repository.get_all_users() if show_inactive_users
                else self.user_repository.get_active_users())
    
    def get_user_roles(self) -> list[str]:
        return [role.value for role in UserRoles]
    
    def get_user_from_email(self, email):
        return self.user_repository.get_user_from_email(email)
    
    def get_user_or_404(self, user_id):
        return self.user_repository.get_user_or_404(user_id)
    
    def create_and_register_user(self, email, password, role):
        """Checks for a unique email before creating user"""
        user = self.user_repository.get_user_from_email(email)
        if not user:
            return self.user_repository.create_and_register_user(email, password, role)
        else:
            raise ValueError(ErrorMessages.EMAIL_NOT_UNIQUE.value)

    def update_user(self, user: User, new_password: str, new_role: Role|str) -> bool:
        """Compares args to user before making changes"""
        changes_made = False
        if new_password:
            if verify_password(new_password, user.password):
                raise ValueError(ErrorMessages.NEW_PW_IS_OLD.value)
            else:
                self.user_repository.update_password(user, new_password)
                changes_made = True
        if new_role not in user.roles:
            self.user_repository.update_role(user, new_role)
            changes_made = True
        return changes_made
    
    def change_user_status(self, user: User) -> str:
        if user.active:
            self.user_repository.deactivate_user(user)
            message = "User deactivated"
        else:
            self.user_repository.activate_user(user)
            message = "User activated"
        return message
    
    def delete_user(self, user: User):
        return self.user_repository.delete_user(user)

    def authenticate_user(self, email: str, password: str) -> User:
        user = user_datastore.find_user(email=email)

        if user and verify_password(password, user.password):
            return user
        else:
            raise ValueError(ErrorMessages.INVALID_LOGIN.value)