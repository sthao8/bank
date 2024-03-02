from datetime import datetime
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
    DecimalField,
    SearchField)
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
    CheckThatTwoFieldsDoNotMatch,
    InputRequiredIfOtherFieldHasSpecificValue)
from constants.constants import BusinessConstants

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
    
class SearchCustomerForm(FlaskForm):
    class Meta:
        csrf = False

    user_defined_fields = ["first_name", "last_name", "city"]

    first_name = StringField(
        "First name",
        render_kw={"placeholder": "Bob", "size": 20},
    )

    last_name = StringField(
        "Last name",
        render_kw={"placeholder": "Bobertson", "size": 20},
    )

    city = StringField(
        "City",
        render_kw={"placeholder": "Stockholm", "size": 20}
    )

    submit = SubmitField("Search")

    @property
    def validation_failed(self):
        return bool(self.errors)

class RegisterCustomerForm(FlaskForm):
    user_defined_fields = [
        "first_name",
        "last_name",
        "address",
        "city",
        "postal_code",
        "birthday",
        "national_id",
        "telephone",
        "email",
        "country"]

    first_name = StringField(
        "First name",
        validators=[Length(min=1, max=50, message="First name cannot exceed 50 characters."),
                    InputRequired()],
        render_kw={"placeholder": "Bob", "size": 20, "autofocus": True}
    )

    last_name = StringField(
        "Last name",
        validators=[Length(min=1, max=50, message="Last name cannot exceed 50 characters."),
                    InputRequired()],
        render_kw={"placeholder": "Robertson", "size": 20}
    )

    address = StringField(
        "Address",
        validators=[Length(min=1, max=50, message="Address cannot exceed 50 characters."),
                    InputRequired()],
        render_kw={"placeholder": "89 Viksängsgatan", "size": 20}
    )

    city = StringField(
        "City",
        validators=[Length(min=1, max=50, message="City cannot exceed 50 characters."),
                    InputRequired()],
        render_kw={"placeholder": "Stockholm", "size": 20}
    )

    postal_code = StringField(
        "Postal code",
        validators=[Length(min=1, max=10, message="Postal code cannot exceed 50 characters."),
                    InputRequired()],
        render_kw={"placeholder": "13245", "size": 20}
    )

    birthday = DateField(
        "Birthday",
        validators=[InputRequired(), Age()],
        render_kw={"placeholder": "YYYY-MM-DD",
                   "max": datetime.now().date().isoformat()}
    )

    national_id = StringField(
        "National id",
        validators=[Length(min=1, max=20, message="National ID cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "123412121234"}
    )

    telephone = TelField(
        "Telephone",
        validators=[Length(min=1, max=20, message="Telephone number cannot exceed 20 characters."), InputRequired()],
        render_kw={"placeholder": "123123 022 55"}
    )

    email = EmailField(
        "Email",
        validators=[Length(min=1, max=50, message="Email cannot exceed 50 characters."), InputRequired()],
        render_kw={"placeholder": "bob.bobertson@mail.com"}
    )

    country = SelectField(
        "Country",
        validate_choice=[InputRequired()]
    )

    submit = SubmitField("Register")

    @property
    def validation_failed(self):
        return bool(self.errors)

class RegisterUserForm(FlaskForm):
    user_defined_fields = ["email", "password", "confirm_password", "role"]

    email = EmailField(
        "Email",
        validators=[InputRequired(), Length(min=1, max=50, message="Email cannot exceed 50 characters.")],
        render_kw={"placeholder": "bob.bobertson@mail.com", "autocomplete": "new-email"}
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[InputRequired(), Length(min=8, max=32, message="Password must be between 8 and 32 characters"), EqualTo("password")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    role = SelectField(
        "Role",
        validators=[InputRequired()]
    )

    submit = SubmitField("Register")

    @property
    def validation_failed(self):
        return bool(self.errors)

class CrudUserForm(FlaskForm):
    user_defined_fields = ["new_password", "confirm_password", "role"]

    new_password = PasswordField(
        "New password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[Optional(strip_whitespace=True), Length(min=8, max=32, message="Password must be between 8 and 32 characters"),
                    EqualTo("new_password")],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    role = SelectField(
        "Role",
        render_kw={"class": "userRole"}
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


class TransactionForm(FlaskForm):
    from_account = SearchField(
        "Account",
        validators=[InputRequired(),
                    Regexp(r'^\d+$', message="Only numbers allowed for account number"),
                    CheckThatTwoFieldsDoNotMatch("to_account", "You have choosen the same account.")],
        render_kw={"placeholder": "Account",
                   "pattern": r'^\d+$',
                   "title": "Only numbers allowed for account number"})
    
    to_account = SearchField(
        "To account",
        validators=[InputRequiredIfOtherFieldHasSpecificValue("type", "transfer"),
                    Regexp(r'^\d+$',message="Only numbers allowed for account number"),
                    CheckThatTwoFieldsDoNotMatch("from_account", "You have choosen the same account.")],
        render_kw={"placeholder": "Account",
                   "pattern": r'^\d+$',
                   "title": "Only numbers allowed for account number"})

    type = SelectField(
        "Type",
        validators=[InputRequired()])

    amount = DecimalField(
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
    
class TransferForm(FlaskForm):
    user_defined_fields = ["account_from", "account_to", "amount"]

    account_from = SelectField(
        "Account from",
        validators=[InputRequired(), CheckThatTwoFieldsDoNotMatch("account_to", "You have choosen the same account.")]
    )

    account_to = SelectField(
        "Account to",
        validators=[InputRequired()]
    )

    amount = DecimalField(
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