from models import User

def get_user(user_email, user_password):
    return User.query.filter_by(email=user_email, password=user_password).one_or_none()
