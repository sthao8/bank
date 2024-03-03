from babel.numbers import format_currency

def string_to_bool(string) -> bool:
    """Turns a string to a boolean. True values are 'on', 'true', and '1'"""
    if string.lower() in ["on", "true", "1"]:
        return True
    return False

def format_money(value, currency="SEK"):
    return format_currency(value, currency, locale="sv_SE")

def get_first_error_message(form_errors: dict):
    """Returns the first error message from form.errors"""
    for error_messages in form_errors.values():
        return error_messages[0]