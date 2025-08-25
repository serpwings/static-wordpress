from tests.test_base import BaseTestCase
from app.models import User
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

    def test_dashboard_access_anonymous(self):
        # Anonymous user should be redirected to login
        response = self.client.get('/index', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_dashboard_access_logged_in(self):
        # Login as regular user
        self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, testuser!', response.data)

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
