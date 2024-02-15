from datetime import date, timedelta
from typing import Any
from flask_wtf import FlaskForm
from wtforms import (
    Form,
    StringField,
    EmailField,
    PasswordField,
    BooleanField,
    TextAreaField,
    IntegerField,
    SubmitField,
    DateField,
    TelField,
    SelectField,
    RadioField,
    DecimalField)
from wtforms.validators import (
    InputRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    Regexp,
    Optional)
from views.validators import (
    Age,
    CheckIfAllPasswordFieldsHaveDataIfOneHasData,
    CheckIfFormHasData)
from business_logic.constants import BusinessConstants

class PrefixedForm(FlaskForm):
    """
    Prefixed forms use a field naming convention of prefix_ + ORM model column 
    name for easier retreival of form data via for looping

    Example:
    field_prefix = "search_"
    search_email = EmailField()
    """
    field_prefix = ""

    @classmethod
    def get_column_name(cls, field_name):
        """Remove prefix and return the ORM model column name"""
        return field_name.removeprefix(cls.field_prefix)

class LoginForm(FlaskForm):
    email = EmailField(
        "email",
        validators=[
            InputRequired(),
            Length(min=5, max=32),
            Email(message="Bad email format")
        ], 
    )
    password = PasswordField(
        "password",
        validators=[
            InputRequired(),
            Length(min=8, max=32, message="Password between 8 and 32 characters")
        ]
    )
    submit = SubmitField("Login")

class SearchAccountForm(FlaskForm):
    search_account_number = StringField(
        "account number",
        render_kw={
            "size": 20,
            "placeholder": "account number",
            "autocomplete": "off",
            "pattern": r'^\d+$',
            "title": "Only numbers allowed for account number",
            "required": True,
        },
        validators=[
            InputRequired(),
            Regexp(r'^\d+$', message="Only numbers allowed for account number")
        ]
    )
    submit = SubmitField("Search")

class SearchCustomerForm(PrefixedForm):
    class Meta:
        csrf = False

    field_prefix = "search_"

    search_first_name = StringField(
        "first name",
        render_kw={"placeholder": "first name", "size": 20}, # you can even put css classes here
    )

    search_last_name = StringField(
        "last name",
        render_kw={"placeholder": "last name", "size": 20}, # you can even put css classes here
    )

    search_city = StringField(
        "city",
        render_kw={"placeholder": "city", "size": 20}
    )

    submit = SubmitField("Search")

class RegisterCustomerForm(PrefixedForm):
    field_prefix = "register_"

    register_first_name = StringField(
        "first name",
        validators=[Length(min=1, max=50, message="First name cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "first name", "size": 20, "autofocus": True}
    )

    register_last_name = StringField(
        "last name",
        validators=[Length(min=1, max=50, message="Last name cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "last name", "size": 20}
    )

    register_address = StringField(
        "address",
        validators=[Length(min=1, max=50, message="Address cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "address", "size": 20}
    )

    register_city = StringField(
        "city",
        validators=[Length(min=1, max=50, message="City cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "city", "size": 20}
    )

    register_postal_code = StringField(
        "postal code",
        validators=[Length(min=1, max=10, message="Postal code cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "postal code", "size": 20}
    )

    #TODO you need a custom check here in js to prevent submission
    register_birthday = DateField(
        "birthday",
        validators=[InputRequired(), Age()],
        render_kw={"placeholder": "birthday"}
    )

    register_national_id = StringField(
        "national id",
        validators=[Length(min=1, max=20, message="National ID cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "national id"}
    )

    register_telephone = TelField(
        "telephone",
        validators=[Length(min=1, max=20, message="Telephone number cannot exceed 20 characters."), InputRequired()],
        render_kw={"placeholder": "telephone"}
    )

    register_email = EmailField(
        "email",
        validators=[Length(min=1, max=50, message="Email cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "email"}
    )

    register_country = SelectField(
        "country",
        validate_choice=[InputRequired()]
    )

    submit = SubmitField("Register")

class RegisterUserForm(PrefixedForm):
    field_prefix = "register_"

    register_email = EmailField(
        "email",
        validators=[InputRequired(), Length(min=1, max=50, message="Email cannot exceed 50 characters.")],
        render_kw={"placeholder": "email", "autocomplete": "new-email"}
    )

    register_password = PasswordField(
        "password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "password", "autocomplete": "new-password"}
    )

    register_confirm_password = PasswordField(
        "conform password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters"), EqualTo("register_password")],
        render_kw={"placeholder": "confirm password", "autocomplete": "new-password"}
    )

    register_role = SelectField(
        "role",
        validators=[InputRequired()]
    )

    submit = SubmitField("Register")

class CrudUserForm(PrefixedForm):
    field_prefix = "crud_"

    crud_new_password = PasswordField(
        "new password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "new password", "autocomplete": "new-password"}
    )

    crud_confirm_password = PasswordField(
        "confirm password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters"),
                    EqualTo("crud_new_password")],
        render_kw={"placeholder": "confirm password", "autocomplete": "new-password"}
    )

    crud_role = SelectField(
        "role",
        validators=[]
    )

    submit_update = SubmitField(
        "Update",
        validators=[CheckIfAllPasswordFieldsHaveDataIfOneHasData(), CheckIfFormHasData()]
    )

    submit_deactivate = SubmitField("Deactivate")

class TransactionForm(PrefixedForm):
    field_prefix = "trans_"

    trans_accounts = SelectField(
        "account",
        validators=[InputRequired()],
        render_kw={"placeholder": "accounts"})

    trans_type = SelectField(
        "type",
        validators=[InputRequired()])

    trans_amount = DecimalField(
        "amount",
        use_locale=False,
        places=2,
        validators=[InputRequired(), NumberRange(min=0, message="deposit/withdrawal amount cannot be less than 0.")],
        render_kw={"placeholder": "amount", "min": 0, "type": "number", "step": "0.01"}
    )

    submit = SubmitField()
    
class TransferForm(PrefixedForm):
    field_prefix = "transfer_"

    account_from = SelectField(
        "account from",
        validators=[InputRequired()]
    )

    account_to = SelectField(
        "account to",
        validators=[InputRequired()]
    )

    transfer_amount = DecimalField(
        "amount",
        places=2,
        use_locale=False,
        validators=[InputRequired(), NumberRange(min=0, message="Transfer amount cannot be less than 0.")],
        render_kw={"placeholder": "amount", "min": 0, "type": "number", "step": "0.01"}
    )

    submit = SubmitField()