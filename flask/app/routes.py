from flask import render_template, flash, redirect, url_for
from app import app
#from app.forms import LoginForm
from flaskext.mysql import MySQL

#from forms import RegisterForm, LoginForm

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'bughound'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


#db = pymysql.connect("localhost", "root", "system", "bughound")


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    
    
    
    
    return render_template('index.html', title='Home', user=user, posts=posts)


#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        flash('Login requested for user {}, remember_me={}'.format(
#            form.username.data, form.remember_me.data))
#        return redirect(url_for('index'))
#    return render_template('login.html',  title='Sign In', form=form)

@app.route('/select')
def select():
#    conn = mysql.connect()
    cursor = mysql.connect().cursor()
    sql = "select * from Employee"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('db.html', results=results)



@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_employee = [
                form.name.data,
                form.username.data,
                bcrypt.generate_password_hash(form.password.data),
                form.userLevel.data
            ]
            try:
                cursor = mysql.connect().cursor()
                sql = "INSERT INTO `Employee` VALUES (null, %s, %s, %s, %s)"
                cursor.execute(sql, (new_employee[0], new_employee[1], new_employee[2], new_employee[4]))
                flash('New employee added.')
                return redirect('/index/')
            except IntegrityError:
                error = 'That Employee already exists.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)






















