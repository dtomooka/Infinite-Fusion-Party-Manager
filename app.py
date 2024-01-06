from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from models import Users, Sessions, Players, Pokemon, PokedexBase, PokedexFusion
import os
from sqlalchemy.orm import DeclarativeBase
from webforms import LoginForm, RegisterForm, CreateSessionForm, SelectSessionForm, SubmitSessionForm, AddPokemonForm
from werkzeug.security import check_password_hash, generate_password_hash

# Load env variables
load_dotenv()

# Create Flask Instance
app = Flask(__name__)

# Config MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

# Create Secret Key
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Initilize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Initialize the app with the extension
with app.app_context():
    db.create_all()


# Index
@app.route("/")
@login_required
def index():
    id = current_user.id 
    current_session = Users.query.get_or_404(id).current_session
    return render_template("index.html", current_session=current_session)


@app.route("/login", methods=["GET", "POST"])
def login():
    logform = LoginForm()
    if logform.validate_on_submit():
        user = Users.query.filter_by(username=logform.username.data).first()
        if user:
            # Check the hash if the user exists
            if check_password_hash(user.hash, logform.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect("/session/select")
        else:
            flash("Incorrect Username or Password - Please Try Again")
    return render_template("login.html", form=logform)
        

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    id = current_user.id
    Users.query.get_or_404(id).current_session = None
    db.session.commit()
    logout_user()
    flash("You have been Logged Out Successfully!")

    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    regform = RegisterForm()
    users = Users.query.order_by(Users.last_login)
    if request.method == "POST":
        if regform.validate_on_submit():
            user = Users.query.filter_by(username=regform.username.data).first()
            # If no user with entered username exits:
            if user is None:
                user = Users(username=regform.username.data, hash=generate_password_hash(regform.password.data, method="pbkdf2", salt_length=16))
                db.session.add(user)
                db.session.commit()
                # Add Flash Message
                flash("User added Successfully!")
                # Query Database for all users ordering by last_login
                users = Users.query.order_by(Users.last_login)
                return redirect("/login")
            # If a user with entered username exists:
            else:
                flash("User already Exists")
            # Clear form
            regform.username.data = ""
            regform.password.data = ""
            regform.password_confirm.data = ""
            return render_template("register.html", users=users, form=regform)
    else:
        print("show register")
        return render_template("register.html", form=regform, users=users)


@app.route("/pokemon/add", methods=["GET", "POST"])
@login_required
def add_pokemon():
    id = current_user.id
    current_session = Users.query.get_or_404(id).current_session
    players = Players.query.filter_by(session_id=current_session)
    # Get new link_id
    link_id = Pokemon.query.filter_by(player_id=players[0].id).order_by(Pokemon.link_id.desc()).first()
    if link_id:
        link_id = link_id + 1
    else:
        print("no pokemon in database")
        link_id = 1
    print("LinkID: ", link_id)

    for key, value in request.form.items():
        print(key, value)
        

        # pokemon_to_add = PokedexBase.query.get_or_404(species=value)

        # pokemon = Pokemon(player_id=key, pokedex_num=pokemon_to_add.pokedex_num, species=value, link_id=link_id, base_id_1=pokemon_to_add.id, type_1=pokemon_to_add.type_1, type_2=pokemon_to_add.type_2)

    return render_template("add_pokemon.html", current_session=current_session, players=players)


@app.route("/user/delete/<int:id>", methods=["GET", "POST"])
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    sessions_to_delete = Sessions.query.filter_by(user_id=id)
    players_to_delete = Players.query.filter_by()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        users = Users.query.order_by(Users.last_login)
    except:
        flash("Error there was a problem try again")
        
    return redirect("/login")


@app.route("/session/create", methods=["GET", "POST"])
@login_required
def create_session():
    form = CreateSessionForm()
    id = current_user.id
    total_session = Sessions.query.filter_by(user_id=id).count()
    players = [{"Player 1": "Player 1 Name"},
               {"Player 2": "Player 2 Name"},
               {"Player 3": "Player 3 Name"},
               {"Player 4": "Player 4 Name"}]
    form = CreateSessionForm(player_names=players)
    if form.validate_on_submit():
        if total_session < 4:
            session_count = total_session + 1
            session = Sessions(user_id=id, session_num=session_count)
            db.session.add(session)
            db.session.commit()
            player_count = 1
            for player in form.player_names:
                if player.player_name.data:
                    new_player = Players(session_id=session.id, player_num=player_count, name=player.player_name.data)
                    db.session.add(new_player)
                    db.session.commit()
                    player_count = player_count + 1
            flash("Session Added Successfully")
            return redirect("/session/select")
        else:
            flash("Already at max session count. Please delete one of your sessions to add another")
            return redirect("/session/select")
    # Clear the Form
    form.player_num.data = ""
    for player in form.player_names:
        player.player_name.data = ""
    form.ruleset.data = ""

    return render_template("create_session.html", form=form)


@app.route("/session/delete/<int:session_id>", methods=["GET", "POST"])
@login_required
def delete_session(session_id):
    id = current_user.id
    session_to_delete = Sessions.query.get_or_404(session_id)
    if id == session_to_delete.user.id or current_user.username == "Admin":
        # Delete all players and pokemon associated with that session
        for player in session_to_delete.players:
            delete_player(player.id)
    
        # Delete the session and commit
        db.session.delete(session_to_delete)
        db.session.commit()
        if current_user.username == "Admin":
            return redirect("/admin/sessions")
        else:
            return redirect("/session/select")
    else:
        flash("You do not have authorization to delete this session")
        return redirect("/session/select")
    

@app.route("/session/select/", methods=["GET", "POST"])
@login_required
def select_session():

    id = current_user.id
    sessions = Sessions.query.filter_by(user_id=id).order_by(Sessions.session_num)
    if request.method == "POST":
        for key in request.form:
            current_session_to_update = Users.query.get_or_404(id)
            current_session_to_update.current_session = int(key)
            db.session.commit()
        return redirect("/")
    return render_template("select_session.html", sessions=sessions)


@app.route("/session/manager", methods=["GET", "POST"])
@login_required
def session_manager():
    id = current_user.id


@app.route("/users", methods=["GET", "POST"])
def users():
    our_users = Users.query.order_by(Users.last_login)
    return render_template("users.html", our_users=our_users)


# Admin Test Pages
@app.route("/admin/sessions", methods=["GET", "POST"])
def admin_sessions():
    sessions = Sessions.query.order_by(Sessions.id)
    return render_template("admin_sessions.html", sessions=sessions)

@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    users = Users.query.order_by(Users.id)
    return render_template("admin_users.html", users=users)

@app.route("/admin/players", methods=["GET", "POST"])
def admin_players():
    players = Players.query.order_by(Players.id)
    return render_template("admin_players.html", players=players)

def user_check(username):
    db.session.execute(db.select())

def delete_all_pokemon_by_player(player_id):
    pokemon_to_delete = Pokemon.query.filter_by(player_id=player_id)
    db.session.delete(pokemon_to_delete)
    db.session.commit()

def delete_player(player_id):
    player_to_delete = Players.query.get_or_404(player_id)
    # delete_all_pokemon_by_player(player_to_delete.id)
    db.session.delete(player_to_delete)
    db.session.commit()


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