from tests.test_base import BaseTestCase
from app.models import User
from app import db

class AdminTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        self.admin = User(username='admin', email='admin@example.com', is_admin=True)
        self.admin.set_password('adminpassword')
        db.session.add(self.user)
        db.session.add(self.admin)
        db.session.commit()

    def test_admin_can_view_user_list(self):
        # Login as admin
        self.client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)
        self.assertIn(b'admin', response.data)

    def test_admin_can_view_user_details(self):
        # Login as admin
        self.client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)
        response = self.client.get(f'/user/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Details for testuser', response.data)

    def test_admin_can_suspend_user(self):
        # Login as admin
        self.client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)

        # Suspend user
        response = self.client.post(f'/user/{self.user.id}/suspend', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User testuser has been suspended', response.data)
        self.assertTrue(self.user.is_suspended)

        # Logout admin
        self.client.get('/logout')

        # Try to login as suspended user
        response = self.client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been suspended.', response.data)

    def test_admin_can_make_admin(self):
        # Login as admin
        self.client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)

        # Make user an admin
        response = self.client.post(f'/user/{self.user.id}/make-admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User testuser is now an admin', response.data)
        self.assertTrue(self.user.is_admin)
