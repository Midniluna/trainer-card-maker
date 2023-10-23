from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, desc, asc, and_, or_, case
from flask import session
from IPython import embed
import datetime
import random

bcrypt = Bcrypt()
db = SQLAlchemy()

API_BASE = "https://pokeapi.co/api/v2/"


class Pokemon(db.Model):
    """Collection of basic info about all pokemon in the known pokedex"""

    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key = True)
    species = db.Column(db.Text, nullable = False)
    # National dex number of that species, regardless of regional variance
    species_dexnum = db.Column(db.String, nullable = True)
    variant_name = db.Column(db.String, nullable = False)
    is_legendary = db.Column(db.Boolean, nullable = False)
    is_mythical = db.Column(db.Boolean, nullable = False)
    sprite = db.Column(db.String, nullable = False)
    shiny_sprite = db.Column(db.String)
    url = db.Column(db.String, nullable = False, unique = True)

    @classmethod
    def sort_pokemon(cls, val = "dex_asc"): 
        """Sort pokemon """
    
        if val == "dex_asc":
            pokemon = db.session.query(cls).order_by(cls.species_dexnum.asc()).order_by(cls.id.asc()).all()

        return pokemon

    
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

    def __repr__(self):
        return f"<User Pokemon id={self.id} species={self.pokemon.species}>"

    __tablename__ = "users_pokemon"

    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(12), nullable = True, default = None)
    is_shiny = db.Column(db.Boolean, nullable = False)
    sprite = db.Column(db.Text)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    favorite = db.Column(db.Boolean, nullable = False, default = False)


    users = db.relationship("User", secondary = 'box', passive_deletes = True)
    pokemon = db.relationship('Pokemon')

    @classmethod
    def sort_pokemon(cls, user_id, val = "oldest"):
        """Simple function that allows a user's pokemon to be sorted given designated parameters. Requires variables user_id and sort value ('oldest' (default), 'newest', 'az', or 'za')
        
        Sorting will always prioritize favorites first, then nicknamed (boolean) pokemon, then inputted sort value."""

        base_query = db.session.query(cls).join(Box, Box.userpkmn_id == cls.id).where(Box.user_id == user_id).order_by(cls.favorite.desc()).order_by(case([(cls.nickname == None, 1)], else_=0))

        if val == "oldest": 
            # Default to "oldest to newest" if val is "oldest" (or no value is specified)
            # Favorites first, then nicknamed pokemon, then from oldest to newest.
            boxed = base_query.order_by(cls.id.asc()).all()
        if val == "newest":
            boxed = base_query.order_by(cls.id.desc()).all()
        elif val == "az":
            boxed = base_query.join(Pokemon, Pokemon.id == cls.pokemon_id).order_by(Pokemon.species.asc()).order_by(cls.id.asc()).all()
        elif val == "za":
            boxed = base_query.join(Pokemon, Pokemon.id == cls.pokemon_id).order_by(Pokemon.species.desc()).order_by(cls.id.asc()).all()

        return boxed

    @staticmethod
    def check_rarity():
        """Check the odds to see if pokemon is common, legendary, or mythic"""

        luckynum = random.randint(0,300)

        if luckynum <= 5:
            return "mythic"
        elif luckynum <= 20:
            return "legendary"
        else: 
            return "common"

    @staticmethod
    def check_shiny():
        """Check the odds to see if generated pokemon is shiny"""
        # shiny odds are typically 1 in 500 not one in 50, but for the sake of a small app that will not have many users or traffic, I'm increasing the odds to 1 in 50 (2 out of 100)

        luckynum = random.randint(1,100)

        if luckynum <= 2:
            return True
        return False
    

    # optional inputs for testing only
    def gen_pokemon(user, shine = None):
        """Generate a new pokemon"""

        # reset user's last-genned pokemon id. Pokemon is deleted from database in app.py /generate route
        if user.last_genned_id is not None:
            user.last_genned_id = None
            db.session.commit()

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

        if shine:
            if pokemon.shiny_sprite is not None:
                sprite = pokemon.shiny_sprite
                genned = UserPkmn(is_shiny = True, sprite = sprite, pokemon_id = pokemon.id)
            else:
                sprite = pokemon.sprite
                genned = UserPkmn(is_shiny = False, sprite = sprite, pokemon_id = pokemon.id)

            db.session.add(genned)
            db.session.commit()
            return genned

        #####################################################################################
            

        if pokemon.shiny_sprite is not None and is_shiny:
            sprite = pokemon.shiny_sprite
        else: 
            sprite = pokemon.sprite
        
        genned = UserPkmn(is_shiny = is_shiny, sprite = sprite, pokemon_id = pokemon.id)
        db.session.add(genned)
        db.session.commit()
        print(f"Pokemon: {pokemon}. Shiny? {is_shiny}. Sprite: {sprite}")

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

    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, nullable = False, unique = True)
    email = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
    bio = db.Column(db.String, nullable = True)
    img_url = db.Column(db.Text, default = '/static/images/default-pic.png')
    # last_catch and last_genned are dates... I think I tried to use the Date type for this but I was having troubles with it
    last_catch = db.Column(db.Text, default = None)
    last_genned = db.Column(db.Text, default = None)
    last_genned_id = db.Column(db.Integer, nullable = True)

    # This user's pokemon. pokemon is deleted upon user deletion, but still may consider revoking that to allow for some type of pokemon-orphanage type deal where users can adopt orphaned pokemon.
    pokemon = db.relationship("UserPkmn", secondary="box", back_populates="users", cascade="all, delete, delete-orphan", single_parent=True)
    card = db.relationship("Card", back_populates="user" , cascade="all, delete, delete-orphan")

    @classmethod
    def signup(cls, username, nickname, password, email):
        """Sign up user. Hashes password and returns user object"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            nickname = nickname,
            username = username,
            email = email,
            password = hashed_pwd
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
    __tablename__ = 'card'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)

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
    
    # I thank StackOverflow every day for giving me this solution for updating this model
    def update(self, kwargs):
        """Simply submit a dictionary where they Keys are column names (i.e. 'slot1_id') and the Values are the desired userpkmn ids"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f"<user id: {self.user_id}, slotted pokemon: {self.return_slotted()}>"


#  ------------------------------------------
#  ------------------------------------------
    

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


