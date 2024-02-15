from flask_wtf import FlaskForm
from sqlalchemy import func, desc, asc

from views.forms import PrefixedForm
from utils import string_to_bool


#TODO maybe make sure that gettattr is a valid sort column instead of relying on user?? 

class SearchResultsHandler():
    """
    Takes flaskform, request.args from a GET request, and the ORM model to query against.
    Has ability to dynamically filter, sort, and order results based on form and args.
    """
    def __init__(self, form: PrefixedForm, args, model) -> None:
        self.form = form
        self.args = args
        self.model = model
        self.previous_sort_col = args.get("previous_sort_col", "id")
        self.current_sort_col = args.get("sort_col", "id")
        self.toggle_order = self.args.get("toggle_order", False, string_to_bool)

    @property
    def page(self) -> int:
        # Reset the page to 1 if a new sort column is clicked or toggle order requested 
        page = self.args.get("page", 1, int)
        if self.current_sort_col != self.previous_sort_col or self.toggle_order:
            page = 1
        return page

    @property
    def sort_order(self) -> str:
        sort_order = self.args.get("sort_order", "asc")

        # Reset the order to ascending if new column clicked, otherwise swap if toggled
        if self.current_sort_col != self.previous_sort_col:
            sort_order = "asc"
        elif self.toggle_order:
            sort_order = "desc" if sort_order == "asc" else "asc"
        return sort_order

    @property
    def query_criteria(self) -> dict:
        """
        Extracts fields with non-empty data from a form with optional fields.
        Returns a dict with orm model column name as key and the corresponding user-input data as value
        """
        query_criteria = {}
        for field_name, field_object in self.form._fields.items():
            if field_name.startswith(self.form.field_prefix) and field_object.data:
                col_name = self.form.get_column_name(field_name)
                query_criteria[col_name] = field_object.data.lower()
        return query_criteria

    @property
    def has_query_criteria(self) -> bool:
        """True if any form fields are not empty """
        return bool(self.query_criteria)

    def _apply_filters(self, query):
        """Apply filters from query criteria onto query based on given args"""
        if self.has_query_criteria:
            for col_name, data in self.query_criteria.items():
                query_col = getattr(self.model, col_name)
                query = query.filter(func.lower(query_col) == data)
        return query

    def _apply_sorting(self, query):
        """Apply sort_by to query based on given args"""
        order_by_col = getattr(self.model, self.current_sort_col)

        if self.sort_order == "asc":
            query = query.order_by(asc(order_by_col))
        elif self.sort_order == "desc":
            query = query.order_by(desc(order_by_col))
        
        return query
    
    def get_paginated_sorted_ordered_results(self, results_per_page=10):
        """Returns sorted and ordered pagination object filtered by optional fields from a form"""
        query = self.model.query
        query= self._apply_filters(query)
        query = self._apply_sorting(query)
        return query.paginate(page=self.page, per_page=results_per_page)