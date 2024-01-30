from flask_wtf import FlaskForm
from wtforms import Form, StringField, EmailField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, EqualTo

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
