from repositories.country_repository import CountryRepository
from models import Country

class CountryService():
    def __init__(self, country_repository: CountryRepository) -> None:
        self.country_repository = country_repository

    def get_country_stats(self):
        return self.country_repository.get_country_stats()
    
    def get_all_countries(self) -> list[Country]:
        return self.country_repository.get_all_countries()

    def calculate_global_stats(self, country_stats):
        return {
            "number_of_customers": sum([country.number_of_customers for country in country_stats]),
            "number_of_accounts": sum([country.number_of_accounts for country in country_stats]),
            "sum_of_accounts": sum([country.sum_of_accounts for country in country_stats])
        }

    def get_country_or_404(self, country_name):
        return self.country_repository.get_country_or_404(country_name)

    def get_form_country_choices(self):
        countries = self.country_repository.get_all_countries()
        return [(country.country_code, country.name) for country in countries]