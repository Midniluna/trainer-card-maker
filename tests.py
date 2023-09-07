# Just for starter tests, will make more files as app expands
from IPython import embed
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
