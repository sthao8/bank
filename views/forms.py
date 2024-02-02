from flask_wtf import FlaskForm
from wtforms import (
    Form,
    StringField,
    EmailField,
    PasswordField,
    BooleanField,
    TextAreaField,
    IntegerField,
    SubmitField)
from wtforms.validators import (
    InputRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    Regexp)

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

class SearchCustomerForm(FlaskForm):
    class Meta:
        csrf = False

    search_first_name = StringField(
        "first name",
        id="search_first_name",
        render_kw={"placeholder": "first name", "size": 20}, # you can even put css classes here
        # validators=[
        #     InputRequired(),
        #     Length(min=2)
        # ]
    )

    search_last_name = StringField(
        "last name",
        id="search_last_name",
        render_kw={"placeholder": "last name", "size": 20}, # you can even put css classes here
        # validators=[
        #     InputRequired(),
        #     Length(min=2)
        # ]
    )

    search_city = StringField(
        "city",
        id="search_city",
        render_kw={"placeholder": "city", "size": 20},
        # validators=(
        #     InputRequired(),
        #     Length(min=1)
        # )
    )

    submit = SubmitField("Search")