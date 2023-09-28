import requests
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional

from sqlalchemy import asc

from IPython import embed

# def gen_choices():
#     """Generate choices for selectfield where key = pokemon species dexnum + name and value = that pokemon's ID"""
#     all_pokemon = Pokemon.query.order_by(asc(Pokemon.id)).all()
#     choices = []
#     for pokemon in all_pokemon:
#         choices.append((pokemon.id, f'#{pokemon.species_dexnum} {pokemon.variant_name}'))
#     return choices
        



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

class GuessPokemon(FlaskForm):
    """Form for guessing generated pokemon"""
    species = StringField("Who's that pokemon?", validators=[InputRequired(message="Please enter a valid pokemon")])

# class EditCardForm(FlaskForm):
#     """Form for editing user's trainer card"""
    
    
class PokemonSelectForm(FlaskForm):
    """Form for selecting pokemon"""

    pokemon = SelectField('Select Pokemon', choices=[])
    nickname = StringField('Enter Nickname', render_kw={"placeholder" : "Nickname (Optional)"})