# File to test new curr_genned

from IPython import embed
from datetime import date
import os
from unittest import TestCase
from flask import g, session, url_for
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

    #    Soooo I've learned that I don't actyally need to add a user here. causes a whole lot of issues.
       

    def tearDown(self):
        db.session.rollback()

        
    def test_signup(self):
        with app.test_client() as client:
            """Test user signup route"""

            # First confirm that password encryption works

            # Try signing up a new user
            # IMPORTANT NOTE: Signup route makes username lowercase to make sure uniqueness check ignores case. if trying to query SQL to find a user, do NOT use username to minimize confusion; use email
            user = User(username = "UserNumberOne", nickname = "xxUserxx", email = "tha_best1@email.com", password = "abc1234")

            res = client.post("/signup", data = {"username" : user.username, "nickname" : user.nickname, "email" : user.email, "password" : user.password, "confirm" : user.password}, follow_redirects = True)
            html = res.get_data(as_text = True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("logout", html)
            self.assertNotIn("login", html)

            check_hashed = User.query.filter_by(email = user.email).first()
            self.assertNotEqual(user.password, check_hashed.password)

            # # Log the user out
            # res2 = client.get("/logout")
            # html2 = res2.get_data(as_text = True)
            # self.assertIn("logged out", html2)
            

    def test_login(self):
        with app.test_client() as client:
            """Test user login route"""
            
            # Set password variable seperately because signup route will hash it
            password = "this is a bad password"
            new_user = User.signup(username = "wubbalubbin", nickname = "wubbzy", email = "wowow_wubbzy@wow.com", password = password)
            db.session.commit()

            # Try logging in as new_user
            res = client.post("/login", data = {"username" : new_user.username, "password" : password}, follow_redirects = True)
            html = res.get_data(as_text = True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome back", html)
            
    def test_username_taken(self):
        with app.test_client() as client:
            """Test signup route for used nicknames"""

            test_user = User.signup(username = "UserRahhh", nickname = "WeirdAl", email = "Yankovich@gmail.com", password = "CheeseSandwhich")
            db.session.commit()

            res2 = client.post("/signup", data={"username" : test_user.username, "nickname" : "nickname", "email" : "imacopy@email.com", "password" : "password", 'confirm' : "password"}, follow_redirects = True)
            html2 = res2.get_data(as_text=True)
            self.assertEqual(res2.status_code, 200)
            self.assertIn("already taken", html2)  

#     def test_edit_user(self):
#         with app.test_client() as client: 
#             """Testing user editing route"""

#             # Add user to database and commit so that user has an id and card exists. signup route didn't do this for some reason
#             db.session.rollback()
#             user = User(username = "Wubbalubbin", nickname = "Wubbzy", email = "Wowow_wubbzy@wow.com", password = "This is a bad password")
#             db.session.add(user)
#             db.session.commit()
#             card = Card(user_id = user.id) 
#             db.session.add(card)
#             db.session.commit()

#             res = client.get(f'profile/{user.id}', follow_redirects = True)
#             html = res.get_data(as_text=True)
#             self.assertEqual(res.status_code, 200)
#             self.assertNotIn('Edit card', html)

#             # User isn't being logged in.... argh. Navbar is still showing "login" and "signup" tabs, and Edit Card button for user profile isn't showing. What am I doing wrong?
#             client.post("/login", data = {"username" : user.username, "password" : user.password}, follow_redirects = True)
            # res2 = client.get(f'profile/{user.id}', follow_redirects = True)
            # html = res2.get_data(as_text=True)
            # self.assertEqual(res2.status_code, 200)

            # self.assertEqual(session[CURR_USER_KEY], user)
            # self.assertIn('Edit', html)
