from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired

#we are going to need some login form for another page so keep for now
#class LoginForm(FlaskForm):
#    username = StringField('Username', validators=[DataRequired()])
#    password = PasswordField('Password', validators=[DataRequired()])
#    remember_me = BooleanField('Remember Me')
#    submit = SubmitField('Sign In')
#    
#    
class EditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    userLevel = IntegerField('User Level', validators=[DataRequired()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')
