# File to test new curr_genned

from IPython import embed
from datetime import date
import os
from unittest import TestCase
from flask import g, url_for
import forms

from models import db, Pokemon, User, UserPkmn, Box, Card

os.environ["DATABASE_URL"] = "postgresql:///pokepals_test"

from app import app, CURR_USER_KEY

db.create_all()

# Make Flask errors be real errors, rather than HTML pages with error info
app.config["TESTING"] = True

# This is a bit of hack, but don"t use Flask DebugToolbar
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
app.config["WTF_CSRF_ENABLED"] = False

# Now tests go here
# python3 -m unittest test_user.py



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

        self.rawpass = password
        self.testuser = user
        
    def tearDown(self):
        db.session.rollback()

        
    def test_signup_login(self):
        with app.test_client() as client:
            """Test user signup + login routes"""

            # First confirm that password encryption works
            self.assertNotEqual(self.rawpass, self.testuser.password)

            # Try logging in as self.testuser
            res = client.post("/login", data = {"username" : self.testuser.username, "password" : self.rawpass}, follow_redirects = True)
            html = res.get_data(as_text = True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome back", html)

            # Try signing up a new user
            res2 = client.post("/signup", data = {"username" : "Wubbalubbin", "nickname" : "Wubbzy", "email" : "Wowow_wubbzy@wow.com", "password" : "This is a bad password"})
            html2 = res.get_data(as_text = True)
            self.assertEqual(res2.status_code, 200)
            self.assertIn("logout", html2)
            self.assertNotIn("login", html2)
            

    def test_username_taken(self):
        with app.test_client() as client:
            """Test to confirm users cannot signup with a username that's already taken"""
            
            new_user = User(username = "Wubbalubbin", nickname = "Wubbzy", email = "Wowow_wubbzy@wow.com", password = "This is a bad password")

            res = client.post("/signup", data={"username" : self.testuser.username, "nickname" : new_user.nickname, "email" : new_user.email, "password" : new_user.password, 'confirm' : new_user.password}, follow_redirects = True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("already taken", html)  
        
    def test_edit_user(self):
        with app.test_client() as client: 
            """Testing user editing route"""

            # Add user to database and commit so that user has an id and card exists. signup route didn't do this for some reason
            db.session.rollback()
            user = User(username = "Wubbalubbin", nickname = "Wubbzy", email = "Wowow_wubbzy@wow.com", password = "This is a bad password")
            db.session.add(user)
            db.session.commit()
            card = Card(user_id = user.id) 
            db.session.add(card)
            db.session.commit()

            res = client.get(f'profile/{user.id}', follow_redirects = True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn('Edit card', html)

            # User isn't being logged in.... argh. Navbar is still showing "login" and "signup" tabs, and Edit Card button for user profile isn't showing. What am I doing wrong?
            client.post("/login", data = {"username" : user.username, "password" : self.rawpass}, follow_redirects = True)
            res2 = client.get(f'profile/{user.id}', follow_redirects = True)
            html = res2.get_data(as_text=True)
            self.assertEqual(res2.status_code, 200)
            self.assertIn('Edit', html)
