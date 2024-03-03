from decimal import Decimal
import unittest
from unittest.mock import Mock

from app import create_app
from constants.constants import TransactionTypes 
from services.transaction_services import TransactionService, TransactionRepository
from services.account_services import AccountService, AccountRepository


class TestTransactions(unittest.TestCase):
    def setUp(self) -> None:
        """ Set up the mock account and transaction service used in all tests"""
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.account_service = AccountService(self.account_repo)
        self.service = TransactionService(self.transaction_repo, self.account_service)
        
        self.mock_account = Mock()
        
        return super().setUp()
    
    def test_1_Value_error_raised_with_negative_withdraw_amount(self):
        transaction_type = TransactionTypes.WITHDRAW
        AMOUNT = Decimal(-5)

        with self.assertRaises(ValueError):
            self.service.process_transaction(self.mock_account, AMOUNT, transaction_type)

    def test_2_Value_error_raised_with_negative_deposit_amount(self):
        transaction_type = TransactionTypes.DEPOSIT
        AMOUNT = Decimal(-5)

        with self.assertRaises(ValueError):
            self.service.process_transaction(self.mock_account, AMOUNT, transaction_type)

    def test_3_Value_error_raised_when_withdrawing_more_than_account_balance(self):
        transaction_type = TransactionTypes.WITHDRAW
        self.mock_account.balance = Decimal(100)
        AMOUNT = Decimal(100.01)

        with self.assertRaises(ValueError):
            self.service.process_transaction(self.mock_account, AMOUNT, transaction_type)

    def test_4_Value_error_raised_when_transferring_more_than_account_balance(self):
        self.mock_account.balance = Decimal(100)
        mock_account_2 = Mock()
        AMOUNT = Decimal(100.01)

        with self.assertRaises(ValueError):
            self.service.process_transfer(self.mock_account, mock_account_2, AMOUNT)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        unittest.main()