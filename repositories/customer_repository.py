from models import Customer, Account, db, Country, Transaction
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload

class CustomerRepository():
    def get_customer_from_id(self, customer_id: int, raise_404: bool) -> Customer|None:
        """get customer from id, use raise_404 to show 404 if customer doesn't exist"""
        query = Customer.query.filter_by(id=customer_id)
        if raise_404:
            return query.one_or_404()
        return query.one_or_none()

    def get_customer_joined_accounts_country_or_404(self, customer_id: int) -> Customer:
        return Customer.query.filter_by(id=customer_id).options(
            joinedload(Customer.accounts),
            joinedload(Customer.country_details)
            ).one_or_404()
    
    def get_customer_from_national_id(self, national_id: str) -> Customer|None:
        return Customer.query.filter_by(national_id=national_id).one_or_none()
    
    def get_all_customers_for_country(self, country: Country) -> list[Customer]:
        return Customer.query.filter_by(country=country.country_code).all()
    
    def get_top_10_customers_for_country(self, country_name: str) -> list[Customer]:
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

    def edit_customer(self, customer: Customer, customer_details: dict) -> None:
        for attribute_name, value in customer_details.items():
            setattr(customer, attribute_name, value)
        db.session.commit()

    def create_customer(self, customer_details: dict) -> Customer:
        """Creates a new customer from customer_details dict,
        which should have all the attribute values needed for Customer objecy"""
        new_customer = Customer()

        for attribute_name, value in customer_details.items():
            setattr(new_customer, attribute_name, value)
        
        db.session.add(new_customer)
        db.session.commit()

        return new_customer