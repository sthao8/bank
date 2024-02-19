from decimal import Decimal
from views.transactions.services import TransactionService
from repositories.transaction_repository import TransactionRepository
from business_logic.constants import TransactionTypes 
import unittest
from unittest.mock import Mock

class TransactionsTest(unittest.TestCase):
    def test_1_Value_error_raised_with_negative_withdraw_amount(self):
        mock_account = Mock()
        mock_account.balance = Decimal(100.00)

        transaction_type = TransactionTypes.WITHDRAW
        amount = Decimal(-5)

        service = TransactionService(TransactionRepository)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, amount, transaction_type)

    def test_2_Value_error_raised_with_negative_deposit_amount(self):
        mock_account = Mock()
        mock_account.balance = Decimal(100.00)

        transaction_type = TransactionTypes.DEPOSIT
        amount = Decimal(-5)

        service = TransactionService(TransactionRepository)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, amount, transaction_type)

    def test_3_Value_error_raised_when_withdrawing_more_than_account_balance(self):
        mock_account = Mock()
        mock_account.balance = Decimal(100.00)

        transaction_type = TransactionTypes.WITHDRAW
        amount = Decimal(100.01)

        service = TransactionService(TransactionRepository)

        with self.assertRaises(ValueError):
            service.process_transaction(mock_account, amount, transaction_type)

    def test_4_Value_error_raised_when_transferring_more_than_account_balance(self):
        mock_account_1 = Mock()
        mock_account_1.balance = Decimal(100.00)

        mock_account_2 = Mock()

        amount = Decimal(100.01)

        service = TransactionService(TransactionRepository)

        with self.assertRaises(ValueError):
            service.process_transfer(mock_account_1, mock_account_2, amount)


if __name__ == "__main__":
    unittest.main()