from .api_models import UserApiModel, CustomerApiModel, TransactionsApiModel
from models import Account
from flask import Blueprint, jsonify, request, url_for
from services.user_services import UserService, UserRepository
from services.customer_services import CustomerService, CustomerRepository
from services.transaction_services import TransactionService, TransactionRepository
from services.account_services import AccountService, AccountRepository

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

user_repo = UserRepository()
user_service = UserService(user_repo)

customer_repo = CustomerRepository()
customer_service = CustomerService(customer_repo)

account_repo = AccountRepository()
account_service = AccountService(account_repo)

transaction_repo = TransactionRepository()
transaction_service = TransactionService(transaction_repo, account_service)

@api_blueprint.route("/user/<int:user_id>")
def user_api(user_id):
    user = user_service.get_user_or_404(user_id)

    user_dict = UserApiModel(user).to_dict()

    return jsonify(user_dict)

@api_blueprint.route("/<int:customer_id>")
def customer_api(customer_id):
    customer = customer_service.get_customer_or_404(customer_id)

    customer_dict = CustomerApiModel(customer).to_dict()

    return jsonify(customer_dict)

@api_blueprint.route("/accounts/<int:account_id>")
def transactions_api(account_id):
    account: Account = account_service.get_account_from_id(account_id, raise_404=True)

    # Make sure offset and limit are not negative
    offset = max(request.args.get("offset", 0, int), 0)
    limit = max(request.args.get("limit", 20, int), 1)

    total_transactions_count = transaction_service.get_count_of_transactions(account_id)

    has_more = offset + limit < total_transactions_count
    if has_more:
        next_url = f"{url_for('api.transactions_api', account_id=account_id, offset=offset + limit, limit=limit, _external=True)}"
    else:
        next_url = None

    account_transactions = transaction_service.get_limited_offset_transactions(account_id, limit, offset)

    transactions_dict = [TransactionsApiModel(transaction).to_dict() for transaction in account_transactions]

    return jsonify({"transactions": transactions_dict,
                    "balance": account.balance,
                    "has_more": has_more,
                    "next": next_url,
                    "offset": offset,
                    "limit": limit,
                     "account_id": account.id })
