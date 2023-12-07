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
app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False

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

        # Trying to debate if adding a user here is even a good idea
        # Much later and still debating it. It doesn't feel like it cut down any of my workload or anything...,
        self.rawpass = "password"
        test_user = User.signup(username = "testuser", nickname = "TestUser", email = "testemail@email.com", password = self.rawpass)
        db.session.commit()

        self.test_user = test_user

    def tearDown(self):
        db.session.rollback()
        
        db.session.delete(self.test_user)
        db.session.commit()
        
        
    def test_signup(self):
        with app.test_client() as client:
            """Test user signup route + make sure their card is created"""

            # Confirm that password encryption works + that UI changes accordingly

            rawpass = "badpass"
            res = client.post("/signup", data = {"username" : "Hiimnew121", "nickname" : "Newbie", "email" : "newbie121@email.com", "password" : rawpass, "confirm" : rawpass}, follow_redirects = True)
            html = res.get_data(as_text = True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("logout", html)
            self.assertNotIn("login", html)
            
            user = User.query.filter_by(email = "newbie121@email.com").first()
            self.assertNotEqual(rawpass, user.password)

            # Card should be created along with new user
            card_exists = Card.query.filter_by(user_id = user.id).one()
            self.assertTrue(card_exists)


    def test_login_logout(self):
        with app.test_client() as client:
            """Test user login route"""

            # Try logging in
            res = client.post("/login", data = {"username" : self.test_user.username, "password" : self.rawpass}, follow_redirects = True)
            html = res.get_data(as_text = True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome back", html)

            # Log the user out
            res2 = client.get("/logout", follow_redirects = True)
            html2 = res2.get_data(as_text = True)
            self.assertIn("alert-success", html2)
            

    def test_username_taken(self):
        with app.test_client() as client:
            """Test signup route for used nicknames"""

            # Should fail if either username or email matches an already in-use one
            # Test username first
            res = client.post("/signup", data={"username" : self.test_user.username, "nickname" : "nickname", "email" : "imacopy@email.com", "password" : "password", 'confirm' : "password"}, follow_redirects = True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("already taken", html)
            
            # Now test email
            res2 = client.post("/signup", data={"username" : "newcopy", "nickname" : "nickname", "email" : self.test_user.email, "password" : "password", 'confirm' : "password"}, follow_redirects = True)
            html2 = res2.get_data(as_text=True)
            self.assertEqual(res2.status_code, 200)
            self.assertIn("already taken", html2)


    def test_delete_user(self):
        with app.test_client() as client: 
            """Test user delete"""

            with client.session_transaction() as sess:
                # First check that no user is in session currently

                user = True if CURR_USER_KEY in sess else False
                self.assertFalse(user)

            # Then make sure you cannot delete a user if you are not signed in as that user
            res = client.post(f"/profile/{self.test_user.id}/delete", follow_redirects = True)
            html = res.get_data(as_text=True)
            self.assertEqual(html, "FALSE")

            # Now signup a user and then make a request to the deletion route
            res2 = client.post("/signup", data={"username" : "deleteme", "nickname" : "deleteddd", "email" : "delete_me@email.com", "password" : "password", 'confirm' : "password"}, follow_redirects = True)
            self.assertIn('/home', res2.request.path)
            
            # User and card exist?
            new_user = User.query.filter_by(username = "deleteme").one()
            card = Card.query.filter_by(user_id = new_user.id).one()
            self.assertIn(card, Card.query.all())
            
            res3 = client.post(f"/profile/{new_user.id}/delete", follow_redirects = True)
            html2 = res3.get_data(as_text=True)
            self.assertEqual(html2, "TRUE")

            # User and card no longer exist?
            self.assertIsNone(User.query.get(new_user.id))
            self.assertNotIn(card, Card.query.all())


    def test_view_edit_user(self):
        with app.test_client() as client: 
            """Test viewing of user edit route"""

            # First make sure page can't be viewed if user is not logged in
            # Anonymous user should be redirected to login upon attempt to enter user edit page
            res = client.get(f"/profile/{self.test_user.id}/edit", follow_redirects = True)
            self.assertIn("/login", res.request.path)

            # Once we know that fails, do it properly. Login then look at the page.
            res2 = client.post("/login", data = {"username" : self.test_user.username, "password" : self.rawpass}, follow_redirects = True)
            self.assertEqual(res2.status_code, 200)

            res3 = client.get(f"/profile/{self.test_user.id}/edit", follow_redirects = True)
            self.assertEqual(res3.status_code, 200)
            self.assertIn(f"/profile/{self.test_user.id}/edit", res3.request.path)


    def test_edit_user(self):
        with app.test_client() as client: 
            """Test post request to user edit route"""
            
            # Login as the test_user
            res = client.post("/login", data = {"username" : self.test_user.username, "password" : self.rawpass}, follow_redirects = True)
            self.assertEqual(res.status_code, 200)
            
            # Edit user
            new_nickname = "UpdatedTestUser"
            new_bio = "Hey look I added some information in here! Radical!"
            
            res2 = client.post(f"/profile/{self.test_user.id}/edit", data={"img_url" : "", "nickname" : new_nickname, "bio" : new_bio}, follow_redirects = True)
            self.assertEqual(res2.status_code, 200)
            self.assertIn(f"/profile/{self.test_user.id}/edit", res2.request.path)

            self.assertEqual(self.test_user.nickname, new_nickname)
            self.assertEqual(self.test_user.bio, new_bio)