# File to test new curr_genned

from IPython import embed
from datetime import date
import os
from unittest import TestCase
from flask import g, url_for
import forms

from models import db, Pokemon, User, UserPkmn, Box, Card

os.environ['DATABASE_URL'] = "postgresql:///pokepals_test"

from app import app, CURR_USER_KEY
from models import CURR_GENNED_KEY

db.create_all()

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

# Now tests go here
# python3 -m unittest test_user_views.py



class UserModelsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.app_context = app.app_context()
        cls.app_context.push()

        # Create all tables in the database
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Remove all tables (except pokemon table, which took a long time to seed) from the database and close the application context
        Box.__table__.drop(db.engine)
        Card.__table__.drop(db.engine)
        UserPkmn.__table__.drop(db.engine)
        User.__table__.drop(db.engine)
        cls.app_context.pop()

    def setUp(self):

        self.client = app.test_client()

        password = "password123"
        user = User.signup(nickname = "Sam", username = "username123", email="loremipsum@email.com", password = password)
        db.session.commit()

        self.rawpass = password
        self.testuser = user
        
    def tearDown(self):
        db.session.rollback()

        
    def test_signup_login(self):
        with app.test_client() as client:
            """Test user signup + login routes"""

            # First confirm that password encryption works
            self.assertNotEqual(self.rawpass, self.testuser.password)

            # Make sure self.testuser is logged out. Then test login route
            client.post('/logout')

            res = client.post('/login', data={'username' : self.testuser.username, 'password' : self.rawpass}, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome back", html)
            
            # Now test signup with existing username. Confirm user signup was failed
            new_user = User(username = 'Wubbalubbin', nickname = 'Wubbzy', email = 'Wowow_wubbzy@wow.com', password = 'This is a bad password')

            res2 = client.post('/signup', data={'username' : self.testuser.username, 'nickname' : new_user.nickname, 'email' :new_user.email, 'password' : new_user.password}, follow_redirects=True)
            html2 = res2.get_data(as_text=True)
            self.assertIn("already taken", html2)
            find_user = User.query.filter_by(id = new_user.id).one_or_none()
            self.assertIsNone(find_user)

            # Try with valid signup info
            res3 = client.post('/signup', data={'username' : 'Wubbalubbin', 'nickname' : 'Wubbzy', 'email' : 'Wowow_wubbzy@wow.com', 'password' : 'This is a bad password'})
            self.assertEqual(res3.status_code, 302)
            found_user = User.query.filter_by(id = self.testuser.id).one_or_none()
            self.assertIsNotNone(found_user)