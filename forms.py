import requests
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional

from sqlalchemy import asc

from IPython import embed


class SignupForm(FlaskForm):
    """User signup form"""
    username = StringField('Enter Username', validators=[InputRequired()])
    nickname = StringField('Enter a nickname', validators=[InputRequired()])
    email = StringField('Enter e-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Enter password', validators=[InputRequired(), Length(min=6)], render_kw={'placeholder': 'Must be at least 6 characters'})

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Enter Username', validators=[InputRequired()])
    password = PasswordField('Enter password', validators=[InputRequired()])

class EditProfileForm(FlaskForm):
    """Form for editing user details"""
    nickname = StringField('Enter new nickname', validators=[Optional()], render_kw={"placeholder" : "Nickname (Optional)"})
    img_url = StringField('Profile picture URL', validators=[Optional()], render_kw={"placeholder" : "URL (Optional)"})

class GuessPokemonForm(FlaskForm):
    """Form for guessing generated pokemon"""
    species = StringField("Who's that pokemon?", validators=[InputRequired(message="Please enter a valid pokemon")])

class EditUserPkmnForm(FlaskForm):
    nickname = StringField('Enter Nickname', validators=[Length(max=12)], render_kw={"placeholder" : "Nickname (Optional)"})


class PokemonSelectForm(FlaskForm):
    """Form for selecting + nicknaming pokemon from list"""
    pokemon = SelectField('Select Pokemon', choices=[])
    nickname = StringField('Enter Nickname', validators=[Length(max=12)], render_kw={"placeholder" : "Nickname (Optional)"})

class PokemonSearchForm(FlaskForm):
    """Form to allow users to search for pokemon by name"""
    search = StringField("Enter Pokemon name:", render_kw={"placeholder" : "Or enter region name for regional variants"})