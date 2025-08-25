from tests.test_base import BaseTestCase
from app.models import User, Account, InvestmentPlan, Investment, Transaction
from app import db

class InvestmentTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
        self.account = Account(account_type='checking', balance=1000.0, user_id=self.user.id)
        self.plan = InvestmentPlan(name='Test Plan', description='A plan for testing.', roi=10.0, duration=30)
        db.session.add(self.account)
        db.session.add(self.plan)
        db.session.commit()

    def test_view_investment_plans(self):
        # Login as user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/investment-plans')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Plan', response.data)

    def test_invest(self):
        # Login as user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

        # Invest 500
        response = self.client.post(f'/invest/{self.plan.id}', data={'amount': 500.0}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have successfully invested $500.00 in Test Plan', response.data)

        # Check account balance
        self.assertEqual(self.account.balance, 500.0)

        # Check investment record
        investment = Investment.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(investment)
        self.assertEqual(investment.amount, 500.0)

        # Check transaction record
        transaction = Transaction.query.filter_by(type='investment').first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, -500.0)

        # Check dashboard for investment
        response = self.client.get('/')
        self.assertIn(b'Test Plan', response.data)
        self.assertIn(b'500.00', response.data)

    def test_invest_insufficient_funds(self):
        # Login as user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

        # Try to invest 1500
        response = self.client.post(f'/invest/{self.plan.id}', data={'amount': 1500.0}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Insufficient funds.', response.data)

        # Check account balance is unchanged
        self.assertEqual(self.account.balance, 1000.0)
