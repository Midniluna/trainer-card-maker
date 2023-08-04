import requests
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional

from IPython import embed


class PokemonSelectForm(FlaskForm):
    """Form for selecting pokemon"""
    pokemon = SelectField('Select Pokemon', choices=[])