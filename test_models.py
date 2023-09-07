# FILE FOR TESTING MODELS

from IPython import embed
from datetime import date
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
# python3 -m unittest tests_models.py


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
        
    def tearDown(self):
        db.session.rollback()


    # def test_user_signup_login(self):



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

        # Clear all tables except Pokemon before each test
        User.query.delete()
        UserPkmn.query.delete()
        Box.query.delete()
        Card.query.delete()

        self.client = app.test_client()
        
    def tearDown(self):
        db.session.rollback()


    def test_user_signup_login(self):
        """Test user signup logic"""

        password = "password123"
        user = User.signup(nickname = "Sam", username = "username123", email="loremipsum@email.com", password = password)
        db.session.commit()

        self.assertNotEqual(password, user.password)
        self.assertEqual(user.bio, None)
        self.assertEqual(user.last_catch, None)

        validated = User.authenticate(user.username, password)
        self.assertIsInstance(validated, User)

    print("User model tests passed")



class UserPkmnModelsTestCase(TestCase):
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

        user = User(nickname = "Micky", username = "Mick-E-Mouse", email="MickeyAndMinnie@email.com", password = "Minnie143")
        
        self.user = user
        db.session.add(user)
        db.session.commit()
        
    def tearDown(self):
        db.session.rollback()


    def test_gen_pokemon(self):

        genned = UserPkmn.gen_pokemon()
        self.assertIsNotNone(genned.sprite)
        self.assertIsNone(genned.nickname)

        # checking to make sure dexnum is always 4 digits long
        id = genned.pokemon_id
        pkmn = Pokemon.query.get(id)
        self.assertEqual(len(pkmn.species_dexnum), 4)

    ########### MUST UNCOMMENT "GUARANTEE SHINY" LOGIC IN MODELS.PY FILE FOR THIS TO RETURN TRUE ###########
                                    # (currently, line #189) #

        for x in range(1,50):
            # Try generating a guaranteed shiny. stating variable first for readability
            shiny = True
            genned2 = UserPkmn.gen_pokemon(shiny)
            # get base pokemon data of genned pokemon
            base = Pokemon.query.get(genned2.pokemon_id)

            # If shiny sprite does not exist, hard-coded shiny-odds fails and generated pokemon is not shiny
            if base.shiny_sprite is None:
                self.assertEqual(genned2.is_shiny, False)
            # If shiny sprite does exist, generated pokemon is indeed shiny
            elif base.shiny_sprite:
                self.assertEqual(genned2.is_shiny, True)
        
        print("Pokemon generator tests passed")



    def test_catch_pokemon(self):
        """Test catching pokemon User method"""
        
        self.assertEqual(self.user.last_catch, None)

        genned = UserPkmn.gen_pokemon()
        species_id = genned.pokemon_id
        check_mon = Pokemon.query.get(species_id)
        species = check_mon.species

        # catch_pokemon function should return "Failed" if incorrect pokemon species is input
        result = User.catch_pokemon(self.user, genned, "wrong pokemon")
        self.assertEqual(result, "Failed")


        # Insert proper inputs, catch_pokemon should pass
        User.catch_pokemon(self.user, genned, species)
        box = Box.query.filter(Box.user_id == self.user.id, Box.userpkmn_id == genned.id).all()
        # Confirm pokemon was caught by checking the pokemon's id and user's id were added to the Box model
        self.assertEqual(len(box), 1)
        self.assertNotEqual(self.user.last_catch, None)


        # Now test for user attempting to catch multiple pokemon on the same day
        genned2 = UserPkmn.gen_pokemon()
        species_id = genned2.pokemon_id
        check_mon = Pokemon.query.get(species_id)
        species = check_mon.species
        # catch_pokemon function should return None if last_catch == today's date, even if given the correct pokemon species
        result2 = User.catch_pokemon(self.user, genned, species)
        self.assertEqual(result2, None)


        print("Catching pokemon tests passed")

        
        
        
        
        # to be continued


        # with app.test_client() as client:


        # nickname username email password (signup(username, email, password) authenticate(username, password)) bio daily_catch