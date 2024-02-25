import random
from datetime import datetime, date
from datetime import timedelta
from decimal import Decimal
from faker import Faker
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

from business_logic.constants import (
    TelephoneCountryCodes,
    TransactionTypes,
    BusinessConstants,
    AccountTypes,
    UserRoles
    )


db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = "Countries"

    country_code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    telephone_country_code = db.Column(db.String(5), unique=False, nullable=False)

    customers = db.relationship("Customer", backref="country_details", lazy=True)

class Customer(db.Model):
    __tablename__= "Customers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), unique=False, nullable=False)
    last_name = db.Column(db.String(50), unique=False, nullable=False)
    address = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    postal_code = db.Column(db.String(10), unique=False, nullable=False)
    birthday = db.Column(db.Date, unique=False, nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    country = db.Column(db.String(2), db.ForeignKey("Countries.country_code"), nullable=False)

    accounts = db.relationship("Account", backref="customer", lazy=True)

class Account(db.Model):
    __tablename__ = "Accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(10), unique=False, nullable=False)
    created = db.Column(db.Date, unique=False, nullable=False)
    balance = db.Column(db.Numeric(15, 2), unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"), nullable=False)

    transactions = db.relationship("Transaction", backref="account", lazy=True)

class Transaction(db.Model):
    __tablename__ = "Transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), unique=False, nullable=False)
    timestamp = db.Column(db.DateTime, unique=False, nullable=False)
    amount = db.Column(db.Numeric(15, 2), unique=False, nullable=False)
    new_balance = db.Column(db.Numeric(15,2), unique=False, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("Accounts.id"), nullable=False)
    checked = db.Column(db.Boolean, nullable=False, default=False)

roles_users = db.Table(
    'RolesUsers',
    db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('Roles.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = "Roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), unique=False,nullable=True)
    active = db.Column(db.Boolean(), nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
