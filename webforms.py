from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FieldList, FormField, IntegerField
from wtforms.validators import DataRequired, EqualTo


# Create Form Class
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords Must Match!")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PlayerNameForm(FlaskForm):
    player_name = StringField("Player Name")

class CreateSessionForm(FlaskForm):
    player_num = SelectField("Number of Players", choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], validators=[DataRequired()])
    player_names = FieldList(FormField(PlayerNameForm), min_entries=1)
    ruleset = SelectField("Ruleset", choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8')])

class SubmitSessionForm(FlaskForm):
    submit = SubmitField("Submit")

class SelectSessionForm(FlaskForm):
    submit = FieldList(FormField(SubmitSessionForm), min_entries=1)

class PokemonForm(FlaskForm):
    player = StringField("Player name", validators=[DataRequired()])

class AddPokemonForm(FlaskForm):
    new_pokemon = FieldList(FormField(PokemonForm), min_entries=1)
    submit = SubmitField("Submit")

