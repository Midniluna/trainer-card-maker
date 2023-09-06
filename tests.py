# Just for starter tests, will make more files as app expands

import os
from unittest import TestCase
from flask import g

from models import db, Pokemon, User, UserPkmn, Box, Card

os.environ['DATABASE_URL'] = "postgresql:///pokepals_test"

from app import app

db.create_all()

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Now tests go here
# python3 -m unittest tests.py

class PokemonModelsTestCase(TestCase):
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
        """Add some basic pokemon to the database"""

        # Clear all tables except Pokemon before each test
        User.query.delete()
        UserPkmn.query.delete()
        Box.query.delete()
        Card.query.delete()

        self.client = app.test_client()

        user = User(nickname = "Sam", username = "username123", email="loremipsum@email.com", password = "password123")
        
        self.user = user
        db.session.add(user)
        db.session.commit()
        
    def tearDown(self):
        db.session.rollback()

    def test_catch_pokemon(self):
        """Test catching pokemon User method"""
        
        self.assertFalse(self.user.daily_catch)
        
        
        
        # to be continued


        # with app.test_client() as client:


        # nickname username email password (signup(username, email, password) authenticate(username, password)) bio daily_catch