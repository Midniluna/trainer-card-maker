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
    """Collection of basic info about all pokemon"""

    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.Text, nullable=False)
    species_dexnum = db.Column(db.Integer, nullable=True)
    variant_name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Pokemon #{self.id}, {self.name}, dexnum: {self.species_dexnum}>"

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


class UserPkmn(db.Model):
    """Details of user's individual pokemon"""

    __tablename__ = "user_pokemon"

    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.Text, db.ForeignKey('pokemon.species'))
    variant = db.Column(db.Text, db.ForeignKey('pokemon.variant_name'))
    nickname = db.Column(db.Text, nullable=True, default=None)


class Party(db.Model):
    """User's Party Pokemon"""

    __tablename__ = 'party'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    pkmn_id = db.Column(db.Integer, db.ForeignKey('user_pokemon.id'))

    def __repr__(self):
        return f"<id: {self.id}, user id: {self.user_id}, pkmn id: {self.pkmn_id}>"
    



def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

