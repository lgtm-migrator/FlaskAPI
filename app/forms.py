from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    school = StringField('School', validators=[DataRequired(), Length(min=2, max=80)])

class ResourceCreation(FlaskForm):
    subject = StringField("Subject Name", validators=[DataRequired(), Length(max=50)])
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])

class SubjectCreation(FlaskForm):
    subject = StringField("Subject Name", validators=[DataRequired(), Length(max=50)])
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])
    