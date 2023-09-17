import os
import datetime
# import requests
# import collections

from flask import Flask, render_template, flash, redirect, request, session, g, url_for, jsonify
from flask_login import LoginManager, login_required

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from flask_debugtoolbar import DebugToolbarExtension

from IPython import embed

# from forms import 
from models import db, connect_db, Pokemon, User, UserPkmn, Box, Card, CURR_GENNED_KEY, serialize_userpkmn
from forms import SignupForm, LoginForm, GuessPokemon

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
        flash("You've already caught a pokemon today!")
        return redirect('/home')
    
    # User has generated a pokemon today but has not caught it
    elif isinstance(can_gen, UserPkmn):
        flash("You have already generated a pokemon today! You may re-attempt to catch it.")
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
    if g.user.id != userid:
        flash('Unauthorized action.', 'danger')
        return redirect('/home')

    else:
        card = Card.query.filter(Card.user_id == userid).one()
        slotted = card.return_slotted()

        return render_template('users/profile.html', user = card.user, all_boxed = card.user.pokemon, slotted = slotted)

##############################################
# CURRENT WIP BELOW. YOU ARE HERE!
############################################## 

@app.route('/card/edit/<int:userid>')
def edit_card(userid):
    """Allow user to modify their card to their liking"""

    if g.user.id != userid:
        flash('Unauthorized action.', 'danger')
        return redirect('/home')

    else:
        card = Card.query.filter(Card.user_id == userid).one()
        slotted = card.return_slotted()
        

        return render_template('/cards/edit-card.html', user = card.user, all_boxed = card.user.pokemon, slotted = slotted, edit = True)
    
@app.route('/card/edit/<int:userid>/submit', methods=["PATCH", "POST"])
def handle_card_edit(userid):
    """Handle's ajax request to for modifying a pokemon"""

    # Okay. Let's see. 
    # Think about this.
    # You're given the pokemon's ID and slot number. 
    id = int(request.json["pkmn_id"])
    slot = int(request.json["slot"])
    card = Card.query.filter(Card.user_id == userid).one()
    userpkmn = UserPkmn.query.get(id)

    pkmn_slot1 = card.slot1_id
    pkmn_slot2 = card.slot2_id
    pkmn_slot3 = card.slot3_id
    pkmn_slot4 = card.slot4_id
    pkmn_slot5 = card.slot5_id
    pkmn_slot6 = card.slot6_id

    embed()

    if request.json["pkmn2_id"] != "None" and request.json["slot2"] != "None":
        id2 = int(request.json["pkmn2_id"])
        slot2 = request.json["slot2"]
        return "yippie"

    # I already know I'm gonna HATE this bc it's gonna look ugly but </3
    if slot == 1:
        card.slot1_id = userpkmn.id
    elif slot == 2:
        card.slot2_id = userpkmn.id
    elif slot == 3:
        card.slot3_id = userpkmn.id
    elif slot == 4:
        card.slot4_id = userpkmn.id
    elif slot == 5:
        card.slot5_id = userpkmn.id
    elif slot == 6:
        card.slot6_id = userpkmn.id

    db.session.commit()

    return jsonify(userpkmn.serialize_userpkmn())

@app.route('/card/edit/<int:userid>/delete', methods=["POST"])
def handle_card_delete(userid):
    """Handle's ajax request to remove a pokemon from their card"""

    slot = int(request.json["slot_id"])
    card = Card.query.filter(Card.user_id == userid).one()

    if slot == 1:
        card.slot1_id = None
    elif slot == 2:
        card.slot2_id = None
    elif slot == 3:
        card.slot3_id = None
    elif slot == 4:
        card.slot4_id = None
    elif slot == 5:
        card.slot5_id = None
    elif slot == 6:
        card.slot6_id = None

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



# This is how to turn data into jsonify-able data for javascript

# def serialize(self):
#         return {
#             "id" : self.id,
#             "flavor" : self.flavor,
#             "size" : self.size,
#             "rating" : self.rating,
#             "image" : self.image
#     }

# then return
# serialized = userpkmn_data.serialize()
# return (jsonify(userpkmn = serialized)

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
    