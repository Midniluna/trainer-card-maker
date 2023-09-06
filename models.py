from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from IPython import embed
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

class Pokemon(db.Model):
    """Collection of basic info about all pokemon in the known pokedex"""

    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.Text, nullable=False)
    # National dex number of that species, regardless of regional variance
    species_dexnum = db.Column(db.Integer, nullable=True)
    variant_name = db.Column(db.String, nullable=False)
    is_legendary = db.Column(db.Boolean, nullable=False)
    is_mythical = db.Column(db.Boolean, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    shiny_sprite = db.Column(db.String)
    url = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Pokemon #{self.id}, {self.variant_name}, dexnum: {self.species_dexnum}>"
    
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
    daily_catch = db.Column(db.Boolean, default = False)

    # This user's pokemon
    pokemon = db.relationship("UserPkmn", secondary="box", backref='user', cascade="all, delete")
    card = db.relationship("Card", cascade="all, delete")

    @classmethod
    def signup(cls, nickname, username, email, password):
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
    
    def catch_pokemon(user, genned, input):
        """Catch pokemon and give the user/trainer ownership of it"""
        
        # if the pokemon species name matches the user's input, add it to the database with the user as the owner.
        if input == genned.species:
            db.session.add(genned)
            db.session.commit()

            new_boxed = Box(user_id = user.id, userpkmn_id = genned.id)
            db.session.add(new_boxed)
            db.session.commit()
        else:
            return False
    

    def __repr__(self):
        return f"<User {self.id}, {self.username}"

#  ------------------------------------------
#  ------------------------------------------

class UserPkmn(db.Model):
    """Each generated pokemon"""

    __tablename__ = "users_pokemon"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.Text, nullable=True, default=None)
    is_shiny = db.Column(db.Boolean, nullable = False)
    sprite = db.Column(db.Text)

    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))

    @classmethod
    def check_rarity(cls):
        """Check the odds to see if pokemon is common, legendary, or mythic"""

        luckynum = random.randint(0,300)

        if luckynum <= 10:
            return "mythic"
        elif luckynum <= 40:
            return "legendary"
        else: 
            return "common"

    @classmethod
    def check_shiny(cls):
        """Check the odds to see if generated pokemon is shiny"""
        # shiny odds are typically 1 in 500 not one in 50, but for the sake of a small app that will not have many users or traffic, I'm increasing the odds to 1 in 50. Also, I could have used "if luckynum == 1" but 25 feels like a luckier number

        luckynum = random.randint(0,50)

        if luckynum == 25:
            return True
        return False
    
    
    def gen_pokemon():
        """Generate a new pokemon"""

        rarity = UserPkmn.check_rarity()
        print(f"Rarity: {rarity}")

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

        print(f"What pokemon: {pokemon.variant_name}")

        sprite = None
        is_shiny = UserPkmn.check_shiny()
        
        # If the pokemon has a shiny sprite AND check_shiny comes out true, sprite is shiny, else return false
        print(f"Does shiny sprite exist? : {bool(pokemon.shiny_sprite)}")
        # ^ show whether or not there's a shiny sprite
        # print(is_shiny) 
        # ^ show results of shiny odds check

        if pokemon.shiny_sprite is not None and is_shiny:
            sprite = pokemon.shiny_sprite
            print("Shiny!")
        else: 
            sprite = pokemon.sprite
            print("Not shiny")
        print(f"Sprite: {sprite}")

        genned = UserPkmn(is_shiny = is_shiny, sprite = sprite, pokemon_id = pokemon.id)
        # Do NOT commit yet; if user cannot correctly guess pokemon, pokemon is not added into database

        return genned

        


#  ------------------------------------------
#  ------------------------------------------

class Box(db.Model):
    
    """Many-to-many table connecting User data, Pokemon data, and each UserPkmn's data"""

    __tablename__ = "box"
    
    # Who owns the pokemon?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    # What's special about this user's pokemon? Nickname? Shiny?
    userpkmn_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='cascade'), primary_key=True)

    def __repr__(self):
        return f"User: {self.user_id} -- Genned pokemon id: {self.userpkmn_id}"

#  ------------------------------------------
#  ------------------------------------------

class Card(db.Model):
    """Trainer card / User's Party Pokemon ; User and their 6 chosen display pokemon"""

    __tablename__ = 'card'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    userpkmn_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id'), primary_key=True)

    def __repr__(self):
        return f"<id: {self.id}, user id: {self.user_id}, pkmn id: {self.userpkmn_id}>"
    



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

