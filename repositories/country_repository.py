from models import Country, Customer, db, Account
from sqlalchemy import func, select, desc
from sqlalchemy.orm import joinedload

class CountryRepository():
    def get_country_or_404(country_name):
        return Country.query.filter(func.lower(Country.name)==country_name.lower()).one_or_404()

    def get_all_countries() -> Country:
        return Country.query.all()
    
    def get_top_10_country_customers(country_name):
        return db.session.execute(
                select(
                Customer, 
                func.count(Account.id).label("number_of_accounts"),
                func.sum(Account.balance).label("sum_of_accounts"))
                .join(Account, Account.customer_id==Customer.id)
                .join(Country, Country.country_code==Customer.country)
                .where(Country.name==country_name)
                .group_by(Customer.id)
                .order_by(desc("sum_of_accounts"))
                .limit(10)
            ).all()
    
    def get_all_country_customers(country_name) -> Country:
        return Country.query.filter_by(
            name=country_name
            ).options(
                joinedload(Country.customers)
                .joinedload(Customer.accounts)
                .joinedload(Account.transactions)
            ).all()

    def get_country_stats():
        return db.session.execute(
            select(
                Country.name,
                func.count(func.distinct(Customer.id)).label("number_of_customers"),
                func.count(Account.id).label("number_of_accounts"),
                func.sum(Account.balance).label("sum_of_accounts"))
                .join(Customer, Customer.country==Country.country_code)
                .join(Account, Account.customer_id==Customer.id)
                .group_by(Customer.country)
                .order_by(desc("sum_of_accounts"))
            ).all()