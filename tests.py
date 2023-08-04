# Just for starter tests, will make more files as app expands

import os
from unittest import TestCase
from flask import g

from models import db

os.environ['DATABASE_URL'] = "postgresql:///pokepals-test"

from app import app

db.create_all()

# Now tests go here
# python3 -m unittest tests.py