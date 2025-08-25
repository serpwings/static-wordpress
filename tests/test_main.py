from tests.test_base import BaseTestCase
from app.models import User, Account, Transaction
from app import db

class MainTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        self.admin = User(username='admin', email='admin@example.com', is_admin=True)
        self.admin.set_password('adminpassword')
        db.session.add(self.user)
        db.session.add(self.admin)
        db.session.commit()
        self.account = Account(account_type='checking', balance=100.0, user_id=self.user.id)
        db.session.add(self.account)
        db.session.commit()

    def test_dashboard_access_anonymous(self):
        # Anonymous user should be redirected to login
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_dashboard_access_logged_in(self):
        # Login as regular user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, testuser!', response.data)
        self.assertIn(b'Checking', response.data)
        self.assertIn(b'100.00', response.data)

    def test_admin_dashboard_access_non_admin(self):
        # Login as regular user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You must be an admin to view this page.', response.data)
        self.assertNotIn(b'Admin Dashboard', response.data)

    def test_admin_dashboard_access_admin(self):
        # Login as admin user
        self.client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_dashboard_displays_transactions(self):
        # Create a transaction
        t = Transaction(amount=50, type='deposit', account_id=self.account.id)
        db.session.add(t)
        db.session.commit()

        # Login as regular user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deposit', response.data)
        self.assertIn(b'50.00', response.data)

    def test_pagination(self):
        # Create more transactions than TRANSACTIONS_PER_PAGE
        for i in range(15):
            t = Transaction(amount=i, type='deposit', account_id=self.account.id)
            db.session.add(t)
        db.session.commit()

        # Login as regular user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Older transactions', response.data)
        self.assertNotIn(b'Newer transactions', response.data)

        # Go to next page
        response = self.client.get('/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Newer transactions', response.data)
        self.assertNotIn(b'Older transactions', response.data)
