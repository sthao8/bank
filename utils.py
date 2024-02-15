from sqlalchemy import func, desc, asc
from flask_wtf import FlaskForm
from babel.numbers import format_currency

def string_to_bool(string) -> bool:
    """Turns a string to a boolean. True values are 'on', 'true', and '1'"""
    if string.lower() in ["on", "true", "1"]:
        return True
    return False

def format_money(value, currency="SEK"):
    return format_currency(value, currency, locale="sv_SE")