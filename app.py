import os
# import requests
# import collections

from flask import Flask, render_template, flash, redirect, request, session, g, url_for
from flask_login import LoginManager, login_required
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension

from IPython import embed

# from forms import 
from models import db, connect_db, Pokemon, User, UserPkmn, Box, Card
from forms import SignupForm

CURR_USER_KEY = "curr_user"
API_BASE = "https://pokeapi.co/api/v2/"

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pokepals'))
    ### comment top part and uncomment bottom part, save, and run seed file again to seed the pokepals_test database
    # os.environ.get('DATABASE_URL', 'postgresql:///pokepals_test'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "What do people even put here honestly")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id) or None

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@app.route('/')
def direct_home():
    return redirect(url_for('homepage'))

@app.route('/home')
def homepage():
    """Example starter page"""

    return render_template('homepage.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Sign up new user and add to database"""

    # If no user signed in, run the rest of the code. Else, return
    if not g.user:
        form = SignupForm()

        if form.validate_on_submit(self, extra_validators=None):
            try:
                user = User.signup(
                    username=form.username.data,
                    nickname=form.nickname.data,
                    email = form.email.data,
                    password=form.password.data
                )
                db.session.commit()
            except IntegrityError:
                flash("Username is already taken", 'danger')
                return render_template('users/signup.html ')
            
            session[CURR_USER_KEY] = user.id

            return redirect('/')
        
        else:
            return render_template('users/signup.html', form = form)
        
    return

@app.route('/login')
def login():
    if g.user:
        return
    else:
        print("Login page")

@app.route('/generate')
def gen_pokemon():

    genned = UserPkmn.gen_pokemon()
    species = Pokemon.query.get(genned.pokemon_id).species

    return render_template('spawn.html', genned = genned, species = species)





# ---------------- HOW TO DO POKEMON SELECT FORM -------------------

    # form = PokemonSelectForm()
    # all_pkmn = Pokemon.query.all()
    
    # for pokemon in all_pkmn:
    #     form.pokemon.choices.append((pokemon.url, f"#{pokemon.dexnum} {pokemon.variant_name}"))

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



    