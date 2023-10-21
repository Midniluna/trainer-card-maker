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
from forms import SignupForm, LoginForm, EditProfileForm, EditUserPkmnForm, GuessPokemonForm, PokemonSelectForm, PokemonSearchForm

CURR_USER_KEY = "curr_user"

API_BASE = "https://pokeapi.co/api/v2/"

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///pokepals')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['TESTING'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "What do people even put here honestly")
# toolbar = DebugToolbarExtension(app)

connect_db(app)

# My only issue is that wil all of this, when I add @login_required in a route, it just brings me to a login route regardless of whether or not I'm logged in, and when I DO login, it redirects to the homepage, and when I try to get back to the route requiring the login, it makes me login again, never letting me into the route I want to get into. I don't really understand why
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def direct_home():
    """Direct to homepage when given base URL"""
    return redirect(url_for('homepage'))


@app.route('/home')
def homepage():
    """Example starter page"""

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
            db.session.rollback()
            flash("Username or email is already taken", 'danger')
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
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page) if next_page else redirect(url_for("homepage"))
            
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


# -------------------------------------------------
# ----- LOGGED-IN USER ROUTES + CARD EDITING ------
# -------------------------------------------------


@app.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    """View user profile"""
    card = Card.query.filter(Card.user_id == user_id).one()

    all_boxed = UserPkmn.sort_pokemon(user_id, "oldest")

    # Sort it so nicknamed pokemon appear first
    index = 0
    while index < len(all_boxed):
            next =  0
            pokemon = all_boxed[index]
            if pokemon.nickname is not None:
                all_boxed.pop(index) #remove pokemon from original index
                all_boxed.insert(next, pokemon) #move it to first index or next index after previously moved one
                next += 1 
            index += 1

    slotted = card.return_slotted()

    return render_template('users/profile.html', user = card.user, all_boxed = all_boxed, slotted = slotted)


@app.route('/profile/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    """View user profile"""
    
    # First check if user exists. If false, redirect to homepage
    user = User.query.get(user_id)
    if not is_user(user_id):
        flash('Unauthorized action.', 'danger')
        return redirect('/home')
    
    default = '/static/images/default-pic.png'
    
    form = EditProfileForm(obj=user)
    form.populate_obj(user)
    # (don't want img_url to show default path if user does not have an icon)
    if form.img_url.data == default:
        form.img_url.data = ""

    if form.validate_on_submit():
        
        img_url = form.img_url.data
        nickname = form.nickname.data
        
        if nickname != "":
            user.nickname = nickname

        if img_url != "":
            user.img_url = img_url
        else:
            user.img_url = default

        user.nickname = form.nickname.data

        db.session.commit()
        # refresh the page
        return redirect(url_for('edit_profile', user_id=user_id))
    
    return render_template("/users/edit-user.html", user=user, form=form)


@app.route('/profile/<int:user_id>/delete')
def confirm_user_delete(user_id):
    """Show page to confirm user deletion"""

    if not is_user(user_id):
        flash('Unauthorized action.', 'danger')
        return redirect('/home')

    return render_template('/users/delete-user.html')


##############################################
# CURRENT WIP BELOW. YOU ARE HERE!
############################################## 


@app.route('/profile/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Route to commit user deletion"""
    
    user = User.query.filter_by(id = user_id).one_or_none()

    if not is_user(user_id):
        return "FALSE"
    elif user == None:
        return "FALSE"
    else:
        do_logout()
        card = Card.query.filter_by(user_id = user_id).one_or_none()
        if CURR_GENNED_KEY in session:
            session.pop(CURR_GENNED_KEY)
        db.session.delete(card)
        db.session.delete(user)
        db.session.commit()
        return "TRUE"

# View + Edit Card

@app.route('/card/edit/<int:user_id>')
def edit_card(user_id):
    """Allow user to modify their card to their liking"""

    if not is_user(user_id):
        flash('Unauthorized action.', 'danger')
        return redirect('/home')

    else:
        card = Card.query.filter(Card.user_id == user_id).one()
        slotted = card.return_slotted()

        all_boxed = UserPkmn.sort_pokemon(user_id, "oldest")
        index = 0
    # Sort it so nicknamed pokemon appear first
        while index < len(all_boxed):
            next =  0
            pokemon = all_boxed[index]
            if pokemon.nickname is not None:
                all_boxed.pop(index)
                all_boxed.insert(next, pokemon)
                next += 1
            index += 1

        

        return render_template('/cards/edit-card.html', user = card.user, all_boxed = all_boxed, slotted = slotted, edit = True)
    
    
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

# View + Edit caught Pokemon

@app.route('/profile/<int:user_id>/edit/<int:userpkmn_id>', methods=["GET", "POST"])
def edit_pokemon(user_id, userpkmn_id):
    """Allow user to customize their pokemon"""

    pokemon = UserPkmn.query.get(userpkmn_id)
    
    # First confirm this user is the owner of the pokemon
    if not g.user or pokemon not in g.user.pokemon:
        flash('Unauthorized action.', 'danger')
        return redirect(f'/profile/{user_id}')
    
    form = EditUserPkmnForm()

    if form.validate_on_submit():

        nickname = form.nickname.data

        if nickname == "":
                pokemon.nickname = None
        else:
                pokemon.nickname = nickname.capitalize()

            
        db.session.commit()

        flash(f"{pokemon.pokemon.species.capitalize()} is now named {pokemon.nickname if pokemon.nickname else pokemon.pokemon.species}!", 'success')
            
    return render_template('pokemon/edit-pokemon.html', form=form, user = g.user, all_boxed = [pokemon], hide_edit = True)
        # return render_template("users/login.html", form=form)
        



# -------------------------------------------------
# ------ POKEMON CATCHING/GENERATING ROUTES -------
# -------------------------------------------------


@app.route('/generate')
# @login_required
def gen_pokemon():
    """Generate one pokemon daily for the user to catch"""
    user = g.user

    t = datetime.datetime.today()
    today = t.strftime('%m/%d/%Y')
    
    form = GuessPokemonForm()
    can_gen = check_can_gen()
    # User has already caught a pokemon today
    if can_gen == False:
        flash("You've already caught a pokemon today!", 'danger')
        return redirect('/home')
    
    # User has generated a pokemon today but has not caught it
    elif isinstance(can_gen, UserPkmn):
        flash("You have already generated a pokemon today! You may re-attempt to catch it.", 'danger')
        can_gen = UserPkmn.query.get(session["curr_genned"])
        species = Pokemon.query.get(can_gen.pokemon_id).species

        return render_template('pokemon/generate.html', genned = can_gen, species = species, user=user, form = form)

    # If the user has neither caught NOR generated a pokemon today, generate a new pokemon
    elif can_gen == True:

        # First check if the user still has a previously uncaught pokemon. If so, delete the pokemon from the database. Might mess around and change this later to add a "pokemon orphanage" or something where unclaimed pokemon can be caught, perhaps also daily. would mean maybe adding a "filter orphaned" function to the UserPkmn model... hmmn...
        if CURR_GENNED_KEY in session:
            last_genned = UserPkmn.query.get(session[CURR_GENNED_KEY])
            db.session.delete(last_genned)
            db.session.commit()
        
        # For guaranteed shiny generation, insert True into gen_pokemon() function
        genned = UserPkmn.gen_pokemon()
        species = Pokemon.query.get(genned.pokemon_id).species

        g.user.last_genned = today
        db.session.commit()
        session[CURR_GENNED_KEY] = genned.id
        
        return render_template('pokemon/generate.html', genned = genned, species = species, user = g.user, form = form)
    

@app.route('/reset', methods=["POST"])
def reset_pokemon():
    """Deletes currently genned pokemon """
    g.user.last_genned = None
    db.session.commit()
    session.pop(CURR_GENNED_KEY)
    return redirect('/generate')


@app.route('/catch/<int:genned_id>', methods=["POST"])
def catch_pokemon(genned_id):
    """User attempts to catch generated pokemon. This is mostly done via a Javascript POST request to this route."""
    
    genned = UserPkmn.query.get(genned_id)
    input = request.json["species"]
    response = g.user.catch_pokemon(g.user, genned, input)

    if response == "Success":
        session.pop(CURR_GENNED_KEY)

    return response

# -------------------------------------------------
# ---------- LOCALSTORAGE CARD MAKER --------------
# -------------------------------------------------


@app.route('/get-choices')
def get_choices():
    """Route to tell PokemonSelectForm what pokemon choices are available via javascript ajax"""

    all_pokemon = Pokemon.sort_pokemon()
    choices = []
    for pokemon in all_pokemon:
        choices.append((pokemon.id, f'#{pokemon.species_dexnum} {pokemon.variant_name}'))

            
@app.route('/new-card', methods=["GET", "POST"])
def new_card():
    """Allow user (logged-in or anon) to create a basic card that will be saved to the localstorage"""

    selectform = PokemonSelectForm()
    searchform = PokemonSearchForm()

    all_pokemon = Pokemon.sort_pokemon()

    choices = [(pokemon.url, f"#{pokemon.species_dexnum} {pokemon.variant_name.capitalize()}") for pokemon in all_pokemon]
    choices.insert(0, ("", "---NONE---"))

    selectform.pokemon.choices = choices
    loop = [num for num in range(1,7)]

    return render_template('cards/local-card.html', form = selectform, searchform = searchform, loop = loop)


@app.route('/search-pokemon', methods=["POST"])
def search_mon():
    """Allow users to search for a given pokemon"""
    input = request.json["input"]
    
    all_pokemon = Pokemon.query.order_by(asc(Pokemon.id)).where(Pokemon.variant_name.like(f'%{input}%')).all()

    response_obj = {}

    for pokemon in all_pokemon:
        # for ex: {'pikachu' : {'dexnum' : #0025} }
        response_obj[pokemon.variant_name] = {'dexnum' : pokemon.species_dexnum, 'sprite' : pokemon.sprite}

    return jsonify(response_obj)





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
    
def is_user(user_id):
    if not g.user or g.user.id != user_id:
        return False
    else:
        return True
    
    
