from flask import render_template, redirect, url_for, Blueprint, flash, request
from flask_security import login_required

from views.forms import SearchAccountForm, SearchCustomerForm
from .search_results_handler import SearchResultsHandler
from services.customer_services import CustomerService, CustomerRepository
from models import Customer


customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo)

search_blueprint = Blueprint("search", __name__)


@search_blueprint.route("/search-account-number", methods=["POST"])
@login_required
def search_account_number():
    form = SearchAccountForm()

    if form.validate_on_submit():
        customer = customer_service.get_customer_or_none(form.search_customer_id.data)

        if customer:
            return redirect(url_for(
                "customers.customer_page",
                active_page="search_customer", #TODO this is not strictly true
                customer_id=customer.id,)
            )
        else:
            flash("No results found!")
            return redirect(url_for("search.search_customer", active_page="search_customer"))
    #TODO actually decide what to do here if they can't validate. maybe front end validation beforehands and then??
    return redirect(url_for("customers.index"))

@search_blueprint.route("/search-customer")
@login_required
def search_customer():
    form = SearchCustomerForm()

    return render_template(
    "search/search_customer.html",
    active_page="search_customer",
    form=form)

@search_blueprint.route("/search-results")
@login_required
def display_search_results():
    form = SearchCustomerForm(request.args)
    handler = SearchResultsHandler(form, request.args, Customer)
    RESULTS_PER_PAGE = 50

    if handler.has_query_criteria:
        customers = handler.get_paginated_sorted_ordered_results(RESULTS_PER_PAGE)

        return render_template(
            "search/search_results.html",
            active_page="search_customer",
            sort_col=handler.current_sort_col,
            sort_order=handler.sort_order,
            form=form,
            customers=customers,
            page=handler.page)
    else:
        return render_template(
            "search/search_results.html",
            active_page="search_customer",
            form=form,
            customers=None)
