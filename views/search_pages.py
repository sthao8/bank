from flask import render_template, redirect, url_for, Blueprint, flash, request
from flask_security import login_required

from forms import SearchCustomerIDForm, SearchCustomerForm
from services.search_service import SearchService
from services.customer_services import CustomerService, CustomerRepository
from services.account_services import AccountService, AccountRepository


account_repo = AccountRepository()
account_service = AccountService(account_repo)

customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo, account_service)

search_blueprint = Blueprint("search", __name__)

@search_blueprint.route("/search-customer-id", methods=["POST"])
@login_required
def search_customer_id():
    form = SearchCustomerIDForm()

    if form.validate_on_submit():
        customer = customer_service.get_customer_from_id(form.customer_id.data)

        if customer:
            return redirect(url_for(
                "customers.customer_page",
                customer_id=customer.id,)
            )
    flash("No results found!")
    return redirect(url_for("search.advanced_search", active_page="search_customer"))

@search_blueprint.route("/advanced-search")
@login_required
def advanced_search():
    form = SearchCustomerForm()

    return render_template(
    "search/search_customer.html",
    active_page="search_customer",
    form=form)

@search_blueprint.route("/search-results")
@login_required
def display_search_results():
    form = SearchCustomerForm(request.args)
    search_service = SearchService(customer_repo, form, request.args)
    RESULTS_PER_PAGE = 50

    if search_service.has_query_criteria:
        customers = search_service.get_sorted_paginated_results(RESULTS_PER_PAGE)

        return render_template(
            "search/search_results.html",
            active_page="search_customer",
            sort_col=search_service.current_sort_col,
            sort_order=search_service.sort_order,
            form=form,
            customers=customers,
            page=search_service.page)
    else:
        return render_template(
            "search/search_results.html",
            active_page="search_customer",
            form=form,
            customers=None)
