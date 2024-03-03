from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField,
    DateField,
    TelField,
    SelectField,
    DecimalField,
    SearchField)
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    NumberRange,
    Regexp,
    Optional)
from validators import (
    Age,
    CheckIfAllPasswordFieldsHaveDataIfOneHasData,
    CheckThatTwoFieldsDoNotMatch,
    InputRequiredIfOtherFieldHasSpecificValue)
from constants.errors_messages import ErrorMessages

class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            InputRequired(),
            Length(min=5, max=32)
        ],
        render_kw={
            "autofocus": True,
            "size": 20
        }
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=8, max=32, message=ErrorMessages.PW_WRONG_LENGTH.value)
        ],
         render_kw={
            "size": 20
        }
    )
    submit = SubmitField("Login")

    @property
    def validation_failed(self):
        return bool(self.errors)

class SearchCustomerIDForm(FlaskForm):
    customer_id = StringField(
        "Customer ID",
        render_kw={
            "size": 20,
            "placeholder": "Customer ID",
            "autocomplete": "off",
            "pattern": r'^\d+$',
            "title": ErrorMessages.ACCOUNT_ID_INT.value,
            "required": True,
        },
        validators=[
            InputRequired(),
            Regexp(r'^\d+$', message=ErrorMessages.ACCOUNT_ID_INT.value)
        ]
    )
    submit = SubmitField("Search")

    @property
    def validation_failed(self):
        return bool(self.errors)
    
class SearchCustomerForm(FlaskForm):
    """
    For use with SearchResultsHandler, in order to add more fields to search by,
    add a field in this form and its fieldname to user_defined_fields. 
    Fields should of course only correspond to columns existing inside of the Customer model!!! 
    """
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
        validators=[InputRequired(),
                    Length(min=1, max=50, message="First name cannot exceed 50 characters.")],
        render_kw={"placeholder": "Bob", "size": 20, "autofocus": True}
    )

    last_name = StringField(
        "Last name",
        validators=[InputRequired(),
                    Length(min=1, max=50, message="Last name cannot exceed 50 characters.")],
        render_kw={"placeholder": "Robertson", "size": 20}
    )

    address = StringField(
        "Address",
        validators=[InputRequired(),
                    Length(min=1, max=50, message="Address cannot exceed 50 characters.")],
        render_kw={"placeholder": "89 Viksängsgatan", "size": 20}
    )

    city = StringField(
        "City",
        validators=[InputRequired(),
                    Length(min=1, max=50, message="City cannot exceed 50 characters.")],
        render_kw={"placeholder": "Stockholm", "size": 20}
    )

    postal_code = StringField(
        "Postal code",
        validators=[InputRequired(),
                    Length(min=1, max=10, message="Postal code cannot exceed 50 characters.")],
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
        validators=[InputRequired(),
                    Length(min=1, max=20, message="National ID cannot exceed 50 characters.")],
        render_kw={"placeholder": "123412121234"}
    )

    telephone = TelField(
        "Telephone",
        validators=[InputRequired(),
                    Length(min=1, max=20, message="Telephone number cannot exceed 20 characters.")],
        render_kw={"placeholder": "123123 022 55"}
    )

    email = EmailField(
        "Email",
        validators=[InputRequired(),
                    Length(min=1, max=50, message="Email cannot exceed 50 characters.")],
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
        validators=[InputRequired(),
                    Length(min=1, max=50, message="Email cannot exceed 50 characters.")],
        render_kw={"autocomplete": "new-email"}
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(),
                    Length(min=8, max=32, message=ErrorMessages.PW_WRONG_LENGTH.value)],
        render_kw={"autocomplete": "new-password"}
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[InputRequired(),
                    Length(min=8, max=32, message=ErrorMessages.PW_WRONG_LENGTH.value),
                    EqualTo("password", message=ErrorMessages.PW_DO_NOT_MATCH.value)],
        render_kw={"autocomplete": "new-password"}
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
        validators=[Optional(strip_whitespace=True),
                    Length(min=8, max=32, message=ErrorMessages.PW_WRONG_LENGTH.value)],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[Optional(strip_whitespace=True),
                    Length(min=8, max=32, message=ErrorMessages.PW_WRONG_LENGTH.value),
                    EqualTo("new_password", message=ErrorMessages.PW_DO_NOT_MATCH.value)],
        render_kw={"placeholder": "********", "autocomplete": "new-password"}
    )

    role = SelectField(
        "Role",
        render_kw={"class": "userRole"}
    )

    submit_update = SubmitField(
        "Update",
        validators=[CheckIfAllPasswordFieldsHaveDataIfOneHasData()]
    )

    @property
    def validation_failed(self):
        return bool(self.errors)


class TransactionForm(FlaskForm):
    from_account = SearchField(
        "Account",
        validators=[InputRequired(),
                    Regexp(r'^\d+$', message=ErrorMessages.ACCOUNT_ID_INT.value),
                    CheckThatTwoFieldsDoNotMatch("to_account",
                                                 message=ErrorMessages.SAME_ACCOUNT.value)],
        render_kw={"placeholder": "Account",
                   "pattern": r'^\d+$',
                   "title": ErrorMessages.ACCOUNT_ID_INT.value})
    
    to_account = SearchField(
        "To account",
        validators=[InputRequiredIfOtherFieldHasSpecificValue("type", "transfer"),
                    Regexp(r'^\d+$',message=ErrorMessages.ACCOUNT_ID_INT.value),
                    CheckThatTwoFieldsDoNotMatch("from_account",
                                                 message=ErrorMessages.SAME_ACCOUNT.value)],
        render_kw={"placeholder": "Account",
                   "pattern": r'^\d+$',
                   "title": ErrorMessages.ACCOUNT_ID_INT.value})

    type = SelectField(
        "Type",
        validators=[InputRequired()])

    amount = DecimalField(
        "Amount",
        use_locale=False,
        places=2,
        validators=[InputRequired(),
                    NumberRange(min=0.01, message=ErrorMessages.NEGATIVE_AMOUNT.value)],
        render_kw={"placeholder": "123.43", "min": 0, "type": "number", "step": "0.01"}
    )

    submit = SubmitField()

    @property
    def validation_failed(self):
        return bool(self.errors)
