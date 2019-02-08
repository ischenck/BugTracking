from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app.forms import EditForm
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/select')
def select():
#    conn = mysql.connect()
    cursor = mysql.connect().cursor()
    sql = "select * from Employee"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('db.html', results=results)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    form = EditForm()
    
    cursor = mysql.connect().cursor()
    sql = "select * from Employee where employeeId="+str(id)
    cursor.execute(sql)
    results = cursor.fetchone()
#    employeeString = 'Employee ID:'+str(results[0]) + ' Name: '+results[1]
    employeeString = results
    
    form.name.data = results[1]
    form.username.data = results[2]
    form.password.data = results[3]
    form.userLevel.data = results[4]
    

    if form.validate_on_submit():
        print('redirect on submit')
        sql = "update Employee set name="+str(form.name.data)+" ,username="+str(form.username.data)+", password="+str(form.password.data)+", level="+str(form.userLevel.data)+" where employeeId="+str(results[0])+";"
        #this needs some catch and redirect if error
        cursor.execute(sql)   
        
        return redirect(url_for('select'))
    return render_template('edit.html', results=employeeString, form=form)

@app.route('/editEmployee/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest



















