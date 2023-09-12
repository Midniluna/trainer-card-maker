import requests
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional

from IPython import embed

class SignupForm(FlaskForm):
    """User signup form"""
    username = StringField('Enter Username', validators=[InputRequired()])
    nickname = StringField('Enter a nickname', validators=[InputRequired()])
    email = StringField('Enter e-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Enter password', validators=[InputRequired(), Length(min=6)], render_kw={'placeholder': 'Must be at least 6 characters'})
    
class PokemonSelectForm(FlaskForm):
    """Form for selecting pokemon"""
    pokemon = SelectField('Select Pokemon', choices=[])