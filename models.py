# Models
# Create Users model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    hash = db.Column(db.String(128))
    sessions = db.relationship("Sessions", backref="user")
    current_session = db.Column(db.Integer)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

# Create Sessions Model
class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    session_num = db.Column(db.Integer)
    players = db.relationship("Players", backref="session")

# Create Players model
class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
    player_num = db.Column(db.Integer)
    name = db.Column(db.String(20))
    pokemon = db.relationship("Pokemon", backref="player")

# Create Pokemon Model
class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Required
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    pokedex_num = db.Column(db.String(9), nullable=False) # Required
    species = db.Column(db.String(30), nullable=False) # Required
    sprite_variant = db.Column(db.String(2)) # Required
    nickname = db.Column(db.String(30)) # Required
    link_id = db.Column(db.Integer) # Required
    route = db.Column(db.String(50)) # Required
    base_id_1 = db.Column(db.Integer, nullable=False) # Required
    base_id_2 = db.Column(db.Integer) # Required
    type_1 = db.Column(db.String(20), nullable=False) # Required
    type_2 = db.Column(db.String(20)) # Required

# Create Base Pokedex Model
class PokedexBase(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Required
    species = db.Column(db.String(30), nullable=False) # Required
    type_1 = db.Column(db.String(20), nullable=False) # Required
    type_2 = db.Column(db.String(20), nullable=True) # Required

# Create Base Pokedex Model
class PokedexFusion(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Required
    pokedex_num = db.Column(db.String(9), nullable=False) # Required
    species = db.Column(db.String(30), nullable=False) # Required
    base_id_1 = db.Column(db.Integer, nullable=False) # Required
    base_id_2 = db.Column(db.Integer, nullable=True) # Required
    type_1 = db.Column(db.String(20), nullable=False) # Required
    type_2 = db.Column(db.String(20), nullable=True) # Required