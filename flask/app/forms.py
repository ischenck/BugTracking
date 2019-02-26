from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Length, InputRequired


#we are going to need some login form for another page so keep for now
#class LoginForm(FlaskForm):
#    username = StringField('Username', validators=[DataRequired()])
#    password = PasswordField('Password', validators=[DataRequired()])
#    remember_me = BooleanField('Remember Me')
#    submit = SubmitField('Sign In')
#    
#    



class EditForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    username = StringField(
        'username',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    userLevel = IntegerField('User Level',
        validators=[NumberRange(1, 4, "User Level must be between 1 and 4")]
    )
    functionalArea = SelectField('Functional Area', validators=[InputRequired()])

class RegisterForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    username = StringField(
        'username',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=1, max=40)]
    )
    userLevel = IntegerField('User Level',
        validators=[NumberRange(1, 4, "User Level must be between 1 and 4")]
    )
    functionalArea = SelectField('Functional Area', validators=[InputRequired()])
