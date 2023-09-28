from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask import session
from IPython import embed
import datetime
import random

bcrypt = Bcrypt()
db = SQLAlchemy()

API_BASE = "https://pokeapi.co/api/v2/"

# I ALWAYS forget this. to create all tables;
# go in ipython and run %run models.py
# from app import app
# app_context = app.app_context()
# app_context.push()
# db.create_all()

CURR_GENNED_KEY = "curr_genned"


class Pokemon(db.Model):
    """Collection of basic info about all pokemon in the known pokedex"""

    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.Text, nullable=False)
    # National dex number of that species, regardless of regional variance
    species_dexnum = db.Column(db.String, nullable=True)
    variant_name = db.Column(db.String, nullable=False)
    is_legendary = db.Column(db.Boolean, nullable=False)
    is_mythical = db.Column(db.Boolean, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    shiny_sprite = db.Column(db.String)
    url = db.Column(db.String, nullable=False, unique=True)
    
    @classmethod
    def filter_common(cls):
        common_mon = cls.query.filter(cls.is_legendary == False, cls.is_mythical == False).all()
        return common_mon
    
    @classmethod
    def filter_legends(cls):
        all_legends = cls.query.filter(cls.is_legendary == True).all()
        return all_legends
    
    @classmethod
    def filter_mythicals(cls):
        all_myths = cls.query.filter(cls.is_mythical == True).all()
        return all_myths

    def __repr__(self):
        return f"<Pokemon #{self.id}, {self.variant_name}, dexnum: {self.species_dexnum}>"


#  ------------------------------------------
#  ------------------------------------------

class Box(db.Model):
    
    """Table connecting User data, Pokemon data, and each UserPkmn's data"""

    __tablename__ = "box"
    
    # Who owns the pokemon?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key = True)
    # What's special about this user's pokemon? Nickname? Shiny?
    userpkmn_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f"<User: {self.user_id} -- Genned pokemon id: {self.userpkmn_id}>"




#  ------------------------------------------
#  ------------------------------------------
class UserPkmn(db.Model):
    """Instance of a generated pokemon"""

    __tablename__ = "users_pokemon"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(12), nullable=True, default=None)
    is_shiny = db.Column(db.Boolean, nullable = False)
    sprite = db.Column(db.Text)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))


    users = db.relationship("User", secondary='box', passive_deletes=True)
    pokemon = db.relationship('Pokemon')

    @classmethod
    def check_rarity(cls):
        """Check the odds to see if pokemon is common, legendary, or mythic"""

        luckynum = random.randint(0,300)

        if luckynum <= 5:
            return "mythic"
        elif luckynum <= 20:
            return "legendary"
        else: 
            return "common"

    @classmethod
    def check_shiny(cls):
        """Check the odds to see if generated pokemon is shiny"""
        # shiny odds are typically 1 in 500 not one in 50, but for the sake of a small app that will not have many users or traffic, I'm increasing the odds to 1 in 50 (2 out of 100)

        luckynum = random.randint(1,100)

        if luckynum <= 2:
            return True
        return False
    

    # optional inputs for testing only
    def gen_pokemon(shine = None):
        """Generate a new pokemon"""

        # remove last generated pokemon from the session if exists
        if CURR_GENNED_KEY in session:
            session.pop(CURR_GENNED_KEY)

        rarity = UserPkmn.check_rarity()

        # filter potential genned mons by decided rarity
        if rarity == "mythic":
            list_mons = Pokemon.filter_mythicals()
        elif rarity == "legendary":
            list_mons = Pokemon.filter_legends()
        else:
            list_mons = Pokemon.filter_common()


        total_mon = len(list_mons) - 1
        random_index = random.randint(0, total_mon)
        pokemon = list_mons[random_index]


        sprite = None
        is_shiny = UserPkmn.check_shiny()

        # print(f"Does shiny sprite exist? : {bool(pokemon.shiny_sprite)}")
        # ^ show whether or not there's a shiny sprite

            ###################### UNCOMMENT THIS SECTION FOR TESTING ######################
                    # edit: actually I honestly don't need to uncomment it at all
                    
        # if "shine" input is true/exists, guarantee genned pokemon is shiny unless there is no shiny sprite. This section is solely for testing purposes

        if shine:
            if pokemon.shiny_sprite is not None:
                sprite = pokemon.shiny_sprite
                return UserPkmn(is_shiny = True, sprite = sprite, pokemon_id = pokemon.id)
            else:
                sprite = pokemon.sprite
                return UserPkmn(is_shiny = False, sprite = sprite, pokemon_id = pokemon.id)

            #####################################################################################
            

        if pokemon.shiny_sprite is not None and is_shiny:
            sprite = pokemon.shiny_sprite
            # print("Shiny!")
        else: 
            sprite = pokemon.sprite
            # print("Not shiny")
        
        genned = UserPkmn(is_shiny = is_shiny, sprite = sprite, pokemon_id = pokemon.id)
        db.session.add(genned)
        db.session.commit()
        print(f"Pokemon: {pokemon}. Shiny? {is_shiny}. Sprite: {sprite}")
        # Do NOT add to session or commit yet; if user cannot correctly guess pokemon, pokemon is not added into database

        return genned
    
    def serialize_userpkmn(self):
        return {
            "sprite" : self.sprite,
            "userpkmn_id" : self.id,
            "species" : self.pokemon.species.capitalize(),
            "nickname" : self.nickname or ""
        }


        
#  ------------------------------------------
#  ------------------------------------------

class User(db.Model):
    """User in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable = False, unique=True)
    password = db.Column(db.Text, nullable=False)
    bio = db.Column(db.String, nullable=True)
    img_url = db.Column(db.Text, default = '/static/images/default-pic.png')
    last_catch = db.Column(db.Text, default = None)
    last_genned = db.Column(db.Text, default = None)

    # This user's pokemon. pokemon is deleted upon user deletion, but still may consider revoking that to allow for some type of pokemon-orphanage type deal where users can adopt orphaned pokemon.
    pokemon = db.relationship("UserPkmn", secondary="box", back_populates="users", cascade="all, delete, delete-orphan", single_parent=True)
    card = db.relationship("Card", back_populates="user" , cascade="all, delete-orphan")

    # slotted = db.relationship("User", secondary="card", primaryjoin=(Card.user_id))

    @classmethod
    def signup(cls, username, nickname, password, email):
        """Sign up user. Hashes password and returns user object"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            nickname=nickname,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    
    @classmethod 
    def authenticate(cls, username, password):
        """Find user with given name and password. If user with matching username and password is found, return user object. If username and password don't match a user, return false."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False
    
    @classmethod 
    def catch_pokemon(cls, user, genned, input):
        """Catch pokemon and give the user/trainer ownership of it. Requires authorized user, generated pokemon, and user input guessing genned pokemon's species"""

        # First check that the user has not already caught a pokemon today
        t = datetime.datetime.today()
        today = t.strftime('%m/%d/%Y')

        if user.last_catch == today:
            return None
        
        # if the pokemon species name matches the user's input, add it tothe   database with the user as the owner.
        pkmn = Pokemon.query.get(genned.pokemon_id)

        if input == pkmn.species:

            # embed()
            new_boxed = Box(user_id = user.id, userpkmn_id = genned.id)
            db.session.add(new_boxed)
            user.last_catch = today
            db.session.commit()
            return "Success"
        else:
            return "Failed"
    

    def __repr__(self):
        return f"<User {self.id}, {self.username}, last catch date: {self.last_catch}>"



#  ------------------------------------------
#  ------------------------------------------


class Card(db.Model):
    """Trainer card / User's Party Pokemon ; User and their 6 chosen display pokemon"""

    # Note: I don't really like how busy this looks, but with my previous iteration, it would have been incredibly hard to keep track of which pokemon is in which slot of the trainer card, and would have likely required a lot more logic in either javascript or Python. I know it's something I could add to the session, but my concern with that is that if the session was cleared somehow (users can manually clear the session... I don't know if there are other things that can?), I wouldn't want their card wiped, so the best solution is to keep it in the database. This way it's also easier to make sure the user does not have the ability to slot more than 6 pokemon at a time, so I don't have to add any logic for that.
    # It just makes the most sense

    __tablename__ = 'card'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE, delete-orphan"), primary_key=True)

    slot1_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)
    slot2_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)
    slot3_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)
    slot4_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)
    slot5_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)
    slot6_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='SET NULL'), nullable=True, default=None)

    user = db.relationship("User", primaryjoin=(User.id == user_id))


    def return_slotted(self):
        """Compile pokemon by user-dictated position on their respective trainer card. Returns list of pokemon ordered by first to sixth slot on given card."""

        allslotted = {"slot1_id" : UserPkmn.query.filter_by(id = self.slot1_id).one_or_none(), "slot2_id" : UserPkmn.query.filter_by(id = self.slot2_id).one_or_none(), "slot3_id" : UserPkmn.query.filter_by(id = self.slot3_id).one_or_none(), "slot4_id" :UserPkmn.query.filter_by(id = self.slot4_id).one_or_none(), "slot5_id" : UserPkmn.query.filter_by(id = self.slot5_id).one_or_none(), "slot6_id" : UserPkmn.query.filter_by(id = self.slot6_id).one_or_none()}

        return allslotted
    
    # HOLY SHIT I DID IT ACTUALLY? THANK YOU STACK OVERFLOW
    # OKAY. 
    def update(self, kwargs):
        """Simply submit a dictionary where they Keys are column names (i.e. 'slot1_id') and they Values are the desired userpkmn ids"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    # Ohhhhh my god. I can't believe that worked. This literally SAVED MY LIFE my code is GORGEOUS now I am in TEARS

    def __repr__(self):
        return f"<user id: {self.user_id}, slotted pokemon: {self.return_slotted()}>"


#  ------------------------------------------
#  ------------------------------------------
    

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


