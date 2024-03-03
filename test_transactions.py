from decimal import Decimal
import unittest
from unittest.mock import Mock

from app import create_app
from constants.constants import TransactionTypes 
from services.transaction_services import TransactionService, TransactionRepository
from services.account_services import AccountService, AccountRepository


class TestTransactions(unittest.TestCase):
    def test_1_Value_error_raised_with_negative_withdraw_amount(self):
        mock_account = Mock()
        AMOUNT = Decimal(-5)
        transaction_type = TransactionTypes.WITHDRAW

        transaction_repo = TransactionRepository()
        account_repo = AccountRepository()
        account_service = AccountService(account_repo)
        service = TransactionService(transaction_repo, account_service)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, AMOUNT, transaction_type)

    def test_2_Value_error_raised_with_negative_deposit_amount(self):
        mock_account = Mock()
        AMOUNT = Decimal(-5)
        transaction_type = TransactionTypes.DEPOSIT
        
        transaction_repo = TransactionRepository()
        account_repo = AccountRepository()
        account_service = AccountService(account_repo)
        service = TransactionService(transaction_repo, account_service)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, AMOUNT, transaction_type)


    def test_3_Value_error_raised_when_withdrawing_more_than_account_balance(self):
        mock_account = Mock()
        mock_account.balance = Decimal(100)
        AMOUNT = Decimal(100.01)
        transaction_type = TransactionTypes.WITHDRAW

        transaction_repo = TransactionRepository()
        account_repo = AccountRepository()
        account_service = AccountService(account_repo)
        service = TransactionService(transaction_repo, account_service)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, AMOUNT, transaction_type)


    def test_4_Value_error_raised_when_transferring_more_than_account_balance(self):
        mock_account_1 = Mock()
        mock_account_1.balance = Decimal(100)
        AMOUNT = Decimal(100.01)

        mock_account_2 = Mock()

        transaction_repo = TransactionRepository()
        account_repo = AccountRepository()
        account_service = AccountService(account_repo)
        service = TransactionService(transaction_repo, account_service)

        with self.assertRaises(ValueError):
            service.process_transfer(mock_account_1, mock_account_2, AMOUNT)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        unittest.main()