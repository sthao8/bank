from models import Country, Customer, db, Account
from sqlalchemy import func, select, desc

class CountryRepository():
    def get_country_or_404(self, country_name: str) -> Country:
        return Country.query.filter(func.lower(Country.name)==country_name.lower()).one_or_404()

    def get_all_countries(self) -> list[Country]:
        return Country.query.all()

    def get_country_stats(self):
        """Get country-level stats for all countries in database:
        country name, number of customers, number of accounts, sum of accounts"""
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
