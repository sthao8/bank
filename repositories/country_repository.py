from models import Country, Customer, db, Account
from sqlalchemy import func, select, desc

class CountryRepository():
    def get_country_or_404(country_name):
        return Country.query.filter(func.lower(Country.name)==country_name.lower()).one_or_404()

    def get_all_countries():
        return Country.query.all()
    
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