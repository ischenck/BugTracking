from flask import render_template, flash, redirect, url_for
from app import app
#from app.forms import LoginForm
from flaskext.mysql import MySQL

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'system'
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
























