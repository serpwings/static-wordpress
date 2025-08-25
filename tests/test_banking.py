from tests.test_base import BaseTestCase
from app.models import User, Account
from app import db

class BankingTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user1 = User(username='user1', email='user1@example.com')
        self.user1.set_password('password')
        self.user2 = User(username='user2', email='user2@example.com')
        self.user2.set_password('password')
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()
        self.account1 = Account(account_type='checking', balance=100.0, user_id=self.user1.id)
        self.account2 = Account(account_type='checking', balance=50.0, user_id=self.user2.id)
        db.session.add(self.account1)
        db.session.add(self.account2)
        db.session.commit()

    def test_deposit(self):
        # Login as user1
        self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)

        # Deposit 50
        response = self.client.post('/deposit', data={'amount': 50.0}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully deposited $50.00', response.data)

        # Check balance
        self.assertEqual(self.account1.balance, 150.0)

    def test_withdraw(self):
        # Login as user1
        self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)

        # Withdraw 30
        response = self.client.post('/withdraw', data={'amount': 30.0}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully withdrew $30.00', response.data)

        # Check balance
        self.assertEqual(self.account1.balance, 70.0)

    def test_withdraw_insufficient_funds(self):
        # Login as user1
        self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)

        # Withdraw 120 (more than balance)
        response = self.client.post('/withdraw', data={'amount': 120.0}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Insufficient funds.', response.data)

        # Check balance is unchanged
        self.assertEqual(self.account1.balance, 100.0)

    def test_transfer(self):
        # Login as user1
        self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)

        # Transfer 25 to user2
        response = self.client.post('/transfer', data={
            'recipient_email': 'user2@example.com',
            'amount': 25.0
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully transferred $25.00 to user2', response.data)

        # Check balances
        self.assertEqual(self.account1.balance, 75.0)
        self.assertEqual(self.account2.balance, 75.0)

    def test_transfer_insufficient_funds(self):
        # Login as user1
        self.client.post('/login', data={'username': 'user1', 'password': 'password'}, follow_redirects=True)

        # Transfer 150 to user2
        response = self.client.post('/transfer', data={
            'recipient_email': 'user2@example.com',
            'amount': 150.0
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Insufficient funds.', response.data)

        # Check balances are unchanged
        self.assertEqual(self.account1.balance, 100.0)
        self.assertEqual(self.account2.balance, 50.0)
