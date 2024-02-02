from sqlalchemy import func, desc, asc
from flask_wtf import FlaskForm

def string_to_bool(string) -> bool:
    """Turns a string to a boolean"""
    if string.lower() in ["on", "true", "1"]:
        return True
    return False
