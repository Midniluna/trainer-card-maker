from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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
    pokemon = db.relationship('UserPkmn', secondary='box', backref='user')

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and returns user object"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
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

    def __repr__(self):
        return f"<User {self.id}, {self.username}"

#  ------------------------------------------
#  ------------------------------------------

class UserPkmn(db.Model):
    """Each pokemon belonging to a user"""

    __tablename__ = "users_pokemon"

    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
    nickname = db.Column(db.Text, nullable=True, default=None)
    is_shiny = db.Column(db.Boolean, nullable = False, default = False)
    sprite = db.Column(db.Text, default = None)

#  ------------------------------------------
#  ------------------------------------------

class Box(db.Model):
    
    """Many-to-many table connecting User data, Pokemon data, and each UserPkmn's data"""

    __tablename__ = "box"
    
    # Who owns the pokemon?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    # What's special about this user's pokemon? Nickname? Shiny?
    userpkmn_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='cascade'), primary_key=True)
    # What is the pokemon? Species? Variant? Legendary?
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), primary_key=True)

#  ------------------------------------------
#  ------------------------------------------

class Card(db.Model):
    """Trainer card / User's Party Pokemon ; User and their 6 chosen display pokemon"""

    __tablename__ = 'card'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    user_pkmn_id = db.Column(db.Integer, db.ForeignKey('users_pokemon.id', ondelete='cascade'), primary_key=True)

    def __repr__(self):
        return f"<id: {self.id}, user id: {self.user_id}, pkmn id: {self.user_pkmn_id}>"
    



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

