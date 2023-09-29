import os
import datetime
# import requests
# import collections

from flask import Flask, render_template, flash, redirect, request, session, g, url_for, jsonify
from flask_login import LoginManager, login_required

from sqlalchemy import and_, or_, asc, desc, select
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension

from IPython import embed

# from forms import 
from models import db, connect_db, Pokemon, User, UserPkmn, Box, Card, CURR_GENNED_KEY
from forms import SignupForm, LoginForm, GuessPokemon, PokemonSelectForm, PokemonSearchForm

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

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def direct_home():
    # embed()
    return redirect(url_for('homepage'))


@app.route('/home')
def homepage():
    """Example starter page"""
    # embed()

    return render_template('homepage.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Sign up new user and add to database"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data.lower(),
                nickname=form.nickname.data,
                email = form.email.data,
                password=form.password.data
            )
            db.session.commit()

            card = Card(user_id = user.id)
            db.session.add(card)
            db.session.commit()
            
        except IntegrityError:
            flash("Username is already taken", 'danger')
            return render_template('users/signup.html', form = form)
            
        do_login(user)
        return redirect('/')
        
    else:
        return render_template('users/signup.html', form = form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login user"""
    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(username=form.username.data.lower(),
                                         password=form.password.data)
        
        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/home")
            
        flash("Invalid Username or Password", "danger")

    return render_template("users/login.html", form=form)
    
@app.route('/logout')
def logout():
    """Handle user logout"""

    if not g.user:
        flash("You are not currently logged in", "danger")
    else:
        do_logout()
        flash("Successfully logged out", "success")

    return redirect('/home')

@app.route('/get-choices')
def get_choices():
    """Route to tell PokemonSelectForm what pokemon choices are available via javascript ajax"""

    all_pokemon = Pokemon.query.order_by(asc(Pokemon.id)).all()
    choices = []
    for pokemon in all_pokemon:
        choices.append((pokemon.id, f'#{pokemon.species_dexnum} {pokemon.variant_name}'))

            
@app.route('/new-card', methods=["GET", "POST"])
def new_card():
    """Allow user (logged-in or anon) to create a basic card that will be saved to the localstorage"""

    selectform = PokemonSelectForm()
    searchform = PokemonSearchForm()

    all_pokemon = Pokemon.query.order_by(asc(Pokemon.id)).all()
    selectform.pokemon.choices = [(pokemon.url, f"#{pokemon.species_dexnum} {pokemon.variant_name.capitalize()}") for pokemon in all_pokemon]

    loop = [num for num in range(1,7)]

    return render_template('cards/local-card.html', form = selectform, searchform = searchform, loop = loop)


# AGH. stuck here

@app.route('/search-pokemon', methods=["GET", "PATCH"])
def search_mon():
    """Allow users to search for a given pokemon"""
    embed()
    input = request.json["input"]
    
    all_pokemon = Pokemon.query.order_by(asc(Pokemon.id)).where(Pokemon.variant_name.like(f'%{input}%')).all()

    response_obj = {}

    for pokemon in all_pokemon:
        # for ex: {'pikachu' : {'dexnum' : #0025} }
        response_obj[pokemon.variant_name] = {'dexnum' : pokemon.dexnum, 'sprite' : pokemon.sprite}

    return jsonify(response_obj)


@app.route('/generate')
# @login_required
def gen_pokemon():
    """Generate one pokemon daily for the user to catch"""

    t = datetime.datetime.today()
    today = t.strftime('%m/%d/%Y')

    form = GuessPokemon()

    can_gen = check_can_gen()
    # embed()

    # User has already caught a pokemon today
    if can_gen == False:
        flash("You've already caught a pokemon today!", 'error')
        return redirect('/home')
    
    # User has generated a pokemon today but has not caught it
    elif isinstance(can_gen, UserPkmn):
        flash("You have already generated a pokemon today! You may re-attempt to catch it.", 'error')
        can_gen = UserPkmn.query.get(session["curr_genned"])
        species = Pokemon.query.get(can_gen.pokemon_id).species

        return render_template('pokemon/generate.html', genned = can_gen, species = species, form = form)

    # If the user has neither caught NOR generated a pokemon today, generate a new pokemon
    elif can_gen == True:

        # First check if the user still has a previously uncaught pokemon. If so, delete the pokemon from the database. Might mess around and change this later to add a "pokemon orphanage" or something where unclaimed pokemon can be caught, perhaps also daily. would mean maybe adding a "filter orphaned" function to the UserPkmn model... hmmn...
        if CURR_GENNED_KEY in session:
            last_genned = UserPkmn.query.get(session[CURR_GENNED_KEY])
            db.session.delete(last_genned)
            db.session.commit()
        
        genned = UserPkmn.gen_pokemon()
        species = Pokemon.query.get(genned.pokemon_id).species

        g.user.last_genned = today
        db.session.commit()
        session[CURR_GENNED_KEY] = genned.id
        
        return render_template('pokemon/generate.html', genned = genned, species = species, form = form)
    

@app.route('/catch/<int:genned_id>', methods=["POST"])
def catch_pokemon(genned_id):
    """User attempts to catch generated pokemon. This is mostly done via a Javascript POST request to this route."""
    
    genned = UserPkmn.query.get(genned_id)
    input = request.json["species"]
    response = g.user.catch_pokemon(g.user, genned, input)

    if response == "Success":
        session.pop(CURR_GENNED_KEY)

    return response


@app.route('/profile/<int:userid>')
# @login_required
def view_profile(userid):
    """View user profile"""
    # if g.user and g.user.id != userid:
    #     flash('Unauthorized action.', 'danger')
    #     return redirect('/home')

    # is_user = False
    # if g.user and g.user.id == userid:
    #     is_user = True
    
    card = Card.query.filter(Card.user_id == userid).one()
    slotted = card.return_slotted()

    return render_template('users/profile.html', user = card.user, all_boxed = card.user.pokemon, slotted = slotted)

@app.route('/card/edit/<int:userid>')
def edit_card(userid):
    """Allow user to modify their card to their liking"""

    if  not g.user or g.user.id != userid:
        flash('Unauthorized action.', 'danger')
        return redirect('/home')

    else:
        card = Card.query.filter(Card.user_id == userid).one()
        slotted = card.return_slotted()
        

        return render_template('/cards/edit-card.html', user = card.user, all_boxed = card.user.pokemon, slotted = slotted, edit = True)
    
    
@app.route('/card/edit/<int:userid>/submit', methods=["PATCH", "POST"])
def handle_card_edit(userid):
    """Handle's ajax request to for modifying a pokemon"""

    id = int(request.json["pkmn_id"])
    slot = request.json["slot"]
    card = Card.query.filter(Card.user_id == userid).one()
    userpkmn = UserPkmn.query.get(id)

    if request.json["slot2"] != "None" and request.json["pkmn2_id"] != "None":
        id2 = int(request.json["pkmn2_id"])
        slot2 = request.json["slot2"]

        # slot1 will now have userpkmn2's id, and slot2 will have userpkmn1's id
        swap_obj = {slot : id2, slot2 : id}
        card.update(swap_obj)

        # now commit changes

        db.session.commit()
        return "yippie"

    else:

        update_slot = {slot : id}
        card.update(update_slot)

        db.session.commit()

        return jsonify(userpkmn.serialize_userpkmn())


@app.route('/card/edit/<int:userid>/delete', methods=["POST"])
def handle_card_delete(userid):
    """Handle's ajax request to remove a pokemon from their card"""

    slot = request.json["slot_id"]
    card = Card.query.filter(Card.user_id == userid).one()

    delete_obj = {slot : None}
    card.update(delete_obj)

    db.session.commit()
    
    return "Success!"


@app.route('/<int:userpkmn_id>/pokemon/edit')
def edit_pokemon(userpkmn_id):
    """Allow user to customize their pokemon"""
    
    pokemon = UserPkmn.query.get(userpkmn_id)
    if pokemon not in g.user.pokemon:
        print("YOU DON'T OWN THIS POKEMON!")
        print("Continue this later. Idk if this is gonna return the way I want it to so I've gotta inspect that a little later")
        return
    return







def check_can_gen():

    t = datetime.datetime.today()
    today = t.strftime('%m/%d/%Y')

    # If the user has neither caught a pokemon nor generated a pokemon today, return true
    if g.user.last_genned != today and g.user.last_catch != today:
        return True

    # If user has already caught a pokemon today, reject request to generate pokemon
    elif g.user.last_catch == today:
        return False
    
    # If user hasn't caught a pokemon today but has generated a pokemon today, return the uncaught pokemon to allow user to reattempt to catch it
    elif g.user.last_genned == today:
        genned = UserPkmn.query.get(session[CURR_GENNED_KEY])
        return genned
    

##############################################
# CURRENT WIP BELOW. YOU ARE HERE!
############################################## 

# def sort_pokemon(order, user_id = None):
#     """Input a keyword for how pokemon should be ordered: 'dex number', 'alphabetical'; and a user_id if applicable. Add addi"""










# Click slot. Make button active. Click chosen pokemon. collect slot data from active button, collect userpkmn id from chosen pokemon, send data to card editing route. Update card slot on database, return data needed to manipulate DOM (sprite, id, species, nickname)

# Will need it to look something like this



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


