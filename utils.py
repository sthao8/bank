from sqlalchemy import func, desc, asc
from flask_wtf import FlaskForm


def extract_query_criteria(form: FlaskForm) -> dict:
    """Extracts query criteria from the form"""
    query_criteria = {}
    for field_name, field in form._fields.items():
        if field_name.startswith("search_") and field.data:
            col_name = field_name.removeprefix("search_")
            query_criteria[col_name] = field.data.lower()
    return query_criteria

def apply_filters(query, query_criteria: dict, orm_model):
    """Apply filters from query criteria onto query"""
    for col_name, data in query_criteria.items():
        query_col = getattr(orm_model, col_name)
        #TODO you can do Customer.first_name.like("%form.search_first_name.data%") instead for fuzzy + lowercase
        query = query.filter(func.lower(query_col) == data)
    return query

def apply_sorting(query, args, orm_model):
    """Apply sort_by to query"""
    previous_sort_col = args.get("previous_sort_col", "id")
    sort_col = args.get("sort_col", "id")
    sort_order = args.get("sort_order", "asc")
    toggle_order = args.get("toggle_order", False)
    
    order_by_col = getattr(orm_model, sort_col)
    
    # Toggle sort order if the same column is clicked, otherwise reset to ascending
    if sort_col == previous_sort_col and toggle_order:
        sort_order = "desc" if sort_order == "asc" else "asc"
    else:
        sort_order = "asc"

    # Apply sort order
    if sort_order == "asc":
        query = query.order_by(asc(order_by_col))
    elif sort_order == "desc":
        query = query.order_by(desc(order_by_col))
    
    return query
