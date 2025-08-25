from tests.test_base import BaseTestCase
from app.models import User
from app import db

class AuthTestCase(BaseTestCase):
    def test_register(self):
        # Register a new user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)

        # Check the user has been created in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.is_admin)

    def test_login_logout(self):
        # First register a user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, testuser!', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Should be redirected to login page
