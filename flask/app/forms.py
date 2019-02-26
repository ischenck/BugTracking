from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Length, InputRequired
from datetime import date
#we are going to need some login form for another page so keep for now
#class LoginForm(FlaskForm):
#    username = StringField('Username', validators=[DataRequired()])
#    password = PasswordField('Password', validators=[DataRequired()])
#    remember_me = BooleanField('Remember Me')
#    submit = SubmitField('Sign In')
#    
#    


class BugReportForm(FlaskForm):
    program = SelectField('Program', validators=[InputRequired()]
        )
    reportType = SelectField("Report Type", choices=[(1, "Coding Error"), 
        (2, "Suggestion"), (3, "Documentation"), 
        (4, "Hardware"), (5, "Query")
        ], validators=InputRequired()
        )
    severity = SelectField("Severity", choices=[(3, "Minor"), 
        (2, "Serious"), 
        (1, "Fatal")], validators=InputRequired()
        )
    summary = StringField("Summary", validators=[DataRequired(), Length(min=1, max=400)]
        )
    reproducable = BooleanField("Reproducable"
        )
    description = StringField("Description", validators=[DataRequired(), Length(min=1, max=400)]
        )
    suggestedFix = StringField("Description", validators=[DataRequired(), Length(min=1, max=400)]
        )
    reportedBy = SelectField('Reported By', validators=[InputRequired()]
        )
    discoveredDate = DateField('Discovered Date', default=date.today
        )
    assignedTo = SelectField('Assigned To', validators=[InputRequired()]
        )
    comments = StringField("comments", validators=[DataRequired(), Length(min=1, max=400)])
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")]
        )
    priority = SelectField("Priority", choices=[(1, "Fix immediately"), 
        (2, "Fix as soon as possible"), (3, "Fix before next milestone"),
        (4, "Fix before release"), (5, "Fix if possible"), 
        (6, "Optional")], validators=InputRequired()
        )
    resolution = SelectField("Resolution", choices=[(1, "Pending"), (2, "Fixed"),
        (3, "Irreproducible"), (4, "Deferred"), (5, "As designed"),
        (6, "Withdrawn by reporter"), (7, "Need more info"),
        (8, "Disagree with suggestion"), (9, "Duplicate")],
        validators=InputRequired()
        )
    resolutionVersion = IntegerField("Resolution Version",
        validators=[NumberRange(1, 4, "Resolution Version must be between 1 and 100")]
        )
    resolvedBy = SelectField("Resolved By", validators=InputRequired()
        )
    resolvedDate = DateField("Resolved Date", default=date.today
        )
    testedBy = SelectField("Tested By", validators=InputRequired()
        )
    testedDate = DateField("Tested Date", default=date.today
        )
    deferred = BooleanField("Deferred"
        )

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
