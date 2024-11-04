from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, BooleanField, TextAreaField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo



class AddItemForm(FlaskForm):
    name =  StringField('Nom du plat', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[DataRequired(), Length(min=5, max=500)])
    price = FloatField('Prix', validators=[DataRequired()])
    image = FileField('Image du plat', validators=[FileAllowed(['jpg', 'png'])])
    available = BooleanField('Disponible')
    submit = SubmitField('Ajouter/Mettre à jour')
    
class ContactForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Envoyer')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')