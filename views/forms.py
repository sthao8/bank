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
    CheckIfFormHasData,
    CheckThatTwoFieldsDoNotMatch)
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
        "Email",
        validators=[
            InputRequired(),
            Length(min=5, max=32),
            Email(message="Unrecognized email format.")
        ],
        render_kw={
            "autofocus": True,
            "size": 20,
            "placeholder": "youremail@mail.com"
        }
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=8, max=32, message="Password must be between 8 and 32 characters")
        ],
         render_kw={
            "size": 20,
            "placeholder": "*******"
        }
    )
    submit = SubmitField("Login")

    @property
    def validation_failed(self):
        return bool(self.errors)

class SearchAccountForm(FlaskForm):
    search_customer_id = StringField(
        "Customer ID",
        render_kw={
            "size": 20,
            "placeholder": "1238",
            "autocomplete": "off",
            "pattern": r'^\d+$',
            "title": "Only numbers allowed for customer id",
            "required": True,
        },
        validators=[
            InputRequired(),
            Regexp(r'^\d+$', message="Only numbers allowed for account number")
        ]
    )
    submit = SubmitField("Search")

    @property
    def validation_failed(self):
        return bool(self.errors)
    
class SearchCustomerForm(PrefixedForm):
    class Meta:
        csrf = False

    field_prefix = "search_"

    search_first_name = StringField(
        "First name",
        render_kw={"placeholder": "Bob", "size": 20},
    )

    search_last_name = StringField(
        "Last name",
        render_kw={"placeholder": "Robertson", "size": 20},
    )

    search_city = StringField(
        "City",
        render_kw={"placeholder": "Stockholm", "size": 20}
    )

    submit = SubmitField("Search")

    @property
    def validation_failed(self):
        return bool(self.errors)

class RegisterCustomerForm(PrefixedForm):
    field_prefix = "register_"

    register_first_name = StringField(
        "First name",
        validators=[Length(min=1, max=50, message="First name cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "Bob", "size": 20, "autofocus": True}
    )

    register_last_name = StringField(
        "Last name",
        validators=[Length(min=1, max=50, message="Last name cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "Robertson", "size": 20}
    )

    register_address = StringField(
        "Address",
        validators=[Length(min=1, max=50, message="Address cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "89 Viksängsgatan", "size": 20}
    )

    register_city = StringField(
        "City",
        validators=[Length(min=1, max=50, message="City cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "Stockholm", "size": 20}
    )

    register_postal_code = StringField(
        "Postal code",
        validators=[Length(min=1, max=10, message="Postal code cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "13245", "size": 20}
    )

    #TODO you need a custom check here in js to prevent submission
    register_birthday = DateField(
        "Birthday",
        validators=[InputRequired(), Age()],
        render_kw={"placeholder": "birthday"}
    )

    register_national_id = StringField(
        "National id",
        validators=[Length(min=1, max=20, message="National ID cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "12341212-1234"}
    )

    register_telephone = TelField(
        "Telephone",
        validators=[Length(min=1, max=20, message="Telephone number cannot exceed 20 characters."), InputRequired()],
        render_kw={"placeholder": "123-123-22-55"}
    )

    register_email = EmailField(
        "Email",
        validators=[Length(min=1, max=50, message="Email cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "Bob.Robertson@mail.com"}
    )

    register_country = SelectField(
        "Country",
        validate_choice=[InputRequired()]
    )

    submit = SubmitField("Register")

    @property
    def validation_failed(self):
        return bool(self.errors)

class RegisterUserForm(PrefixedForm):
    field_prefix = "register_"

    register_email = EmailField(
        "Email",
        validators=[InputRequired(), Length(min=1, max=50, message="Email cannot exceed 50 characters.")],
        render_kw={"placeholder": "Bob.Robertson@mail.com", "autocomplete": "new-email"}
    )

    register_password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    register_confirm_password = PasswordField(
        "Confirm password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters"), EqualTo("register_password")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    register_role = SelectField(
        "Role",
        validators=[InputRequired()]
    )

    submit = SubmitField("Register")

    @property
    def validation_failed(self):
        return bool(self.errors)

class CrudUserForm(PrefixedForm):
    field_prefix = "crud_"

    crud_new_password = PasswordField(
        "New password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    crud_confirm_password = PasswordField(
        "Confirm password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters"),
                    EqualTo("crud_new_password")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    crud_role = SelectField(
        "Role",
        validators=[]
    )

    submit_update = SubmitField(
        "Update",
        validators=[CheckIfAllPasswordFieldsHaveDataIfOneHasData(), CheckIfFormHasData()]
    )

    submit_deactivate = SubmitField("Deactivate")

    submit_activate = SubmitField("Activate")

    @property
    def validation_failed(self):
        return bool(self.errors)


class TransactionForm(PrefixedForm):
    field_prefix = "trans_"

    trans_accounts = SelectField(
        "Account(s)",
        validators=[InputRequired()],
        render_kw={"placeholder": "accounts"})

    trans_type = SelectField(
        "Type",
        validators=[InputRequired()])

    trans_amount = DecimalField(
        "Amount",
        use_locale=False,
        places=2,
        validators=[InputRequired(), NumberRange(min=0.01, message="deposit/withdrawal amount cannot be less than 0.")],
        render_kw={"placeholder": "123.43", "min": 0, "type": "number", "step": "0.01"}
    )

    submit = SubmitField()

    @property
    def validation_failed(self):
        return bool(self.errors)
    
class TransferForm(PrefixedForm):
    field_prefix = "transfer_"

    transfer_account_from = SelectField(
        "Account from",
        validators=[InputRequired(), CheckThatTwoFieldsDoNotMatch("transfer_account_to", "You have choosen the same account.")]
    )

    transfer_account_to = SelectField(
        "Account to",
        validators=[InputRequired(), CheckThatTwoFieldsDoNotMatch("transfer_account_from", "You have choosen the same account.")]
    )

    transfer_amount = DecimalField(
        "Amount",
        places=2,
        use_locale=False,
        validators=[InputRequired(), NumberRange(min=0.01, message="Transfer amount cannot be less than 0.")],
        render_kw={"placeholder": "123.43", "min": 0, "type": "number", "step": "0.01"}
    )

    submit = SubmitField()

    @property
    def validation_failed(self):
        return bool(self.errors)