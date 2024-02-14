from models import User

def get_user_from_email(user_email):
    return User.query.filter_by(email=user_email).one_or_none()
