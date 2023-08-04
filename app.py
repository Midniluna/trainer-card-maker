import os
import requests
import collections

from flask import Flask, render_template, flash, redirect, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from IPython import embed

# from forms import 
from models import db, connect_db, Pokemon
from forms import PokemonSelectForm

CURR_USER_KEY = "curr_user"
API_BASE = "https://pokeapi.co/api/v2/"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pokepals'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/', methods=['GET', 'POST'])
def load_home():
    """Example starter page"""

    return render_template('base.html')





# ---------------- HOW TO DO POKEMON SELECT FORM -------------------

    # form = PokemonSelectForm()
    # all_pkmn = Pokemon.query.all()
    
    # for pokemon in all_pkmn:
    #     form.pokemon.choices.append((pokemon.url, f"#{pokemon.dexnum} {pokemon.name}"))

    # if form.validate_on_submit():
    #     url = form.pokemon.data
    #     r = requests.get(url)
    #     data = r.json()
    #     pokemon = {"pkmn_img" : data["sprites"]["front_default"], "dexnum" : data["id"]}
    #     return render_template('base.html', form = form, pokemon = pokemon)
    
    # return render_template('base.html', form = form)




# @app.route('/pokemon/<int:dexnum>', methods=['POST'])
# def load_pokemon():
#     pokemon = request.form["pokemon"]
#     r = requests.get(pokemon)
#     data = r.json()



    