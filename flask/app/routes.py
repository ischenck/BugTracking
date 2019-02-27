from flask import Flask, render_template, flash, redirect, url_for, jsonify, request
from app import app
from app.forms import EditForm, RegisterForm, BugReportForm
from flaskext.mysql import MySQL
from functools import wraps

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'system'
app.config['MYSQL_DATABASE_DB'] = 'bughound'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

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
    con = mysql.connect()
    cursor = con.cursor()

    sql = "select * from Employee where employeeId="+str(id)
    cursor.execute(sql)
    results = cursor.fetchone()
    employeeString = results

    sql = "SELECT * FROM FunctionalArea"
    cursor.execute(sql)
    functionalAreaResults = list(cursor.fetchall())
    areas = [i[0] for i in functionalAreaResults]

    # put employee's current functional area on top of list
    print(areas)
    areas.insert(0, areas.pop(areas.index(results[5])))
    # make list of tuples to pass to wtf-form's SelectField (value, display)
    areas_list=[(i, i) for i in areas]

    if request.method == 'GET':      
        form.name.data = results[1]
        form.username.data = results[2]
        form.password.data = ""
        form.userLevel.data = results[4]
        form.functionalArea.choices = areas_list
    elif request.method == 'POST':
        form.functionalArea.choices = areas_list
        if form.validate_on_submit():
            print('redirect on submit')
            editedEmployee = (
                str(form.name.data), 
                str(form.username.data), 
                str(form.password.data), 
                str(form.userLevel.data),
                str(form.functionalArea.data),)
            try:
                sql = "UPDATE Employee SET name=%s, username=%s, password=%s, level=%s, area=%s WHERE employeeId="+str(id)
                cursor.execute(sql, editedEmployee)
                con.commit()
                flash('Employee information updated.')
                return redirect(url_for('select'))
            except Exception as e:
                print("Problem editing Employee in db: " + str(e))
                return redirect(url_for('select'))
    
    return render_template('edit.html', results=employeeString, form=form)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM FunctionalArea"
    cursor.execute(sql)
    areas = cursor.fetchall()
    areas_list=[(str(i[0]), str(i[0])) for i in areas]
    form.functionalArea.choices = areas_list
    if request.method == 'POST':
        form.functionalArea.choices = areas_list
        if form.validate_on_submit():
            newEmployee = (
                str(form.name.data), 
                str(form.username.data), 
                str(form.password.data), 
                str(form.userLevel.data), 
                str(form.functionalArea.data),
                )
            try:
                sql = "INSERT INTO Employee (name, username, password, level, area) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, newEmployee)
                con.commit()
                flash('New employee added.')
                return redirect(url_for('select'))
            except Exception as e:
                flash("Problem inserting into db: " + str(e))
                return redirect(url_for('register'))

    return render_template('register.html', form=form, error=error)



@app.route('/editEmployee/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest


@app.route('/bugreport/', methods=['GET', 'POST'])
def bugReport():
    error = None
    form = BugReportForm(request.form)
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM Program"
    cursor.execute(sql)

    programs = cursor.fetchall()
    programNames =  [(i[1], i[1]) for i in programs]
    programVersions = [(i[2], i[2]) for i in programs]
    programReleaseNumbers = [(i[3], i[3]) for i in programs]
    form.programName.choices = programs
    form.programVersion.choices = programVersions
    form.programReaseNumber.choices = programReleaseNumbers

    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)

    employees = cursor.fetchall()

    form.reportedBy.choices = employees
    form.assignedTo.choices = employees
    form.resolvedBy.choices = employees
    form.testedBy.choices = employees

    if request.method == 'POST':
        form.programName.choices = programs
        form.programVersion.choices = programVersions
        form.programReaseNumber.choices = programReleaseNumbers       
        form.reportedBy.choices = employees
        form.assignedTo.choices = employees
        form.resolvedBy.choices = employees
        form.testedBy.choices = employees
        if form.validate_on_submit():
            program = [program for program in programs 
                if program[1] == form.programName.data and
                program[2] == form.programVersion.data and
                program[3] == form.programReleaseNumber.data
                ]
            programId = program[0][0]
            bugReportData = (
                str(programId),
                str(form.reportType.data),
                str(form.severity.data),
                str(form.summary.data),
                str(form.reproducable.data),
                str(form.description.data),
                str(form.suggestedFix.data),
                str(form.reportedBy.data),
                str(form.discoveredData.data),
                str(form.assignedTo.data),
                str(form.comments.data),
                str(form.status.data),
                str(form.priority.data),
                str(form.resolution.data),
                str(form.resolutionVersion.data),
                str(form.resolvedBy.data),
                str(form.resolvedDate.data),
                str(form.testedBy.data),
                str(form.testedDate.data),
                str(form.deferred.data)
                )
            try:
                sql = "INSERT INTO BugReport (programId, reportType, severity, summary, \
                    reproducable, description, suggestedFix, reportedBy, discoveredDate, \
                    assignedTo, comments, status, priority, resolution, \
                    resolutionVersion, resolvedBy, resolvedDate, testedBy, testedDate, deferred) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                cursor.execute(sql, BugReportData)
                con.commit()
                flash('New Bug Report added')
                return redirect(url_for('bugreport'))
            except Exception as e:
                flash("Problem inserting into db: " + str(e))
                return redirect(url_for('bugreport'))
            
            return render_template('bugreport.html', form=form, error=error)














