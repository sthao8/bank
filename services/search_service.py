from forms import SearchCustomerForm
from utils import string_to_bool
from repositories.customer_repository import CustomerRepository


class SearchService():
    """
    Prepares data from a SearchCustomerForm and request.args
    before calling repository layer to return paginated, sorted, filtered results
    """
    def __init__(self, customer_repo: CustomerRepository, form: SearchCustomerForm, request_args) -> None:
        self.customer_repo = customer_repo
        self.form = form
        self.request_args = request_args
        # Get these static attributes from url params
        self.previous_sort_col = request_args.get("previous_sort_col", "id")
        self.current_sort_col = request_args.get("sort_col", "id")
        self.toggle_order = request_args.get("toggle_order", False, string_to_bool)

    # Set these following dynamic properties based on certain conditions
    @property
    def page(self) -> int:
        # Reset the page to 1 if a new sort column is clicked or same sort column clicked again 
        page = self.request_args.get("page", 1, int)
        if self.current_sort_col != self.previous_sort_col or self.toggle_order:
            page = 1
        return page

    @property
    def sort_order(self) -> str:
        sort_order = self.request_args.get("sort_order", "asc")

        # Reset the order to ascending if new column clicked, otherwise swap if toggled
        if self.current_sort_col != self.previous_sort_col:
            sort_order = "asc"
        elif self.toggle_order:
            sort_order = "desc" if sort_order == "asc" else "asc"
        return sort_order

    @property
    def query_criteria(self) -> dict:
        """Extracts non-empty user-defined fields into a dict."""
        query_criteria = {}
        for field_name, field_object in self.form._fields.items():
            if field_name in self.form.user_defined_fields and field_object.data:
                query_criteria[field_name] = field_object.data.lower()
        return query_criteria

    @property
    def has_query_criteria(self) -> bool:
        """True if any form fields contain data to filter by"""
        return bool(self.query_criteria)

    def get_sorted_paginated_results(self, results_per_page: int=10):
        return self.customer_repo.get_paginated_sorted_search_results(
            self.query_criteria,
            self.current_sort_col,
            self.sort_order,
            self.page,
            results_per_page
        )