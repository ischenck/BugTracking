from flask import Flask, render_template, flash, redirect, url_for, jsonify, request
from app import app
from app.forms import EditForm, RegisterForm, BugReportForm
from flaskext.mysql import MySQL
from functools import wraps
import os
import base64
#from utils import *
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



@app.route('/bug_report/', methods=['GET', 'POST'])
def bug_report():
    error = None
    form = BugReportForm(request.form)
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM Program"
    cursor.execute(sql)

    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"
    programList = [(i[0], (programStr % i[1:4])) for i in programs]

    form.program.choices = programList

    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)

    employees = cursor.fetchall()

    form.reportedBy.choices = employees
    form.assignedTo.choices = employees
    form.resolvedBy.choices = employees
    form.testedBy.choices = employees
    if  request.method == 'GET':
        return render_template('bug_report.html', form=form, error=error)
    if form.validate_on_submit():
        reproducable = int(str(form.reproducable.data) == 'True')
        deferred = int(str(form.deferred.data) == 'True')
        bugReportData = (
            str(form.program.data),
            str(form.reportType.data),
            str(form.severity.data),
            str(form.summary.data),
            str(reproducable),
            str(form.description.data),
            str(form.suggestedFix.data),
            str(form.reportedBy.data),
            str(form.discoveredDate.data),
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
            str(deferred)
            )
        try:
            sql = "INSERT INTO BugReport (programId, reportType, severity, summary, \
                reproducable, description, suggestedFix, reportedBy, discoveredDate, \
                assignedTo, comments, status, priority, resolution, \
                resolutionVersion, resolvedBy, resolvedDate, testedBy, testedDate, deferred) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            cursor.execute(sql, bugReportData)
            con.commit()
            print('New Bug Report added')
            return redirect(url_for('bug_report'))
        except Exception as e:
            print("Problem inserting into db: " + str(e))
            return redirect(url_for('bug_report'))
            
    return render_template('bug_report.html', form=form, error=error)

'''
@app.route('/_get_program_info/')
def _get_program_info():
    programName = request.args.get('programName', '01', type=str)
    print(programName)
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT version, releaseNumber FROM Program WHERE name = %s"
    cursor.execute(sql, str(programName))
    info = cursor.fetchall()
    print(info)
    return jsonify(info)
'''




@app.route('/upload')
def upload_file():
   return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload():
    error = None
    #form = RegisterForm(request.form)
    if request.method == 'POST':
      f = request.files['inputFile']
      f.save(os.path.join('temp_file/',f.filename))
      
      con = mysql.connect()
      cursor = con.cursor()      
      newUpload = (
                str('1'),
                str(f.filename), 
                read_file(os.path.join('temp_file/',f.filename))
                )
                
      sql = "INSERT INTO Attachment (reportId, fileName, file) VALUES (%s, %s, %s)"
      
      try:
          cursor.execute(sql, newUpload)
          con.commit()
          flash('New employee added.')
      except Exception as e:
          flash("Problem inserting into db: " + str(e))
          os.remove(os.path.join('temp_file/',f.filename))
          con.close()
          return redirect(url_for('upload'))

      #clean file
      os.remove(os.path.join('temp_file/',f.filename))
      con.close()  
      return redirect(url_for('index'))          
  
    else: flash('nothing')
    return render_template('upload.html')

'''
Select all from the attachment table and place
results in a table in attachments.html.
'''
@app.route('/attachments')
def attachments():
    cursor = mysql.connect().cursor()
    sql = "select * from Attachment"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        flash("Problem getting files: " + str(e))
    return render_template('attachments.html', results=results)

'''
When a file gets selected in attachments.html
the <report> number and the <file> name are passed here.
Then, this function selects that specific file and
renders it in view_attachment.html.
'''
@app.route('/showFile/<report>/<file>')
def showFile(report,file):
    cursor = mysql.connect().cursor()
     
    sql = "select * from Attachment where reportId=%s and fileName=%s"
    selectAttachment = (
                str(report), 
                str(file)) 
    res = list()        
    try:
        cursor.execute(sql,selectAttachment)
        results = cursor.fetchall()    
    except Exception as e:
        flash("Problem getting files: " + str(e))
    
    #results should only return 1 item in [0]
    #where [0][1] is the file name and [0][2] is the binary file
    write_file(results[0][2],results[0][1])
    res.append(results[0][1])
    file_ = results[0][1]
    
    if results[0][1].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
#        res.append(base64.decodestring(results[0][2]))
        res.append(results[0][1])
    else:
        path = 'app/static/'+file_
        text = open(path, 'r+')
        res.append(text.read())
        text.close()
    
#    res.append(os.path.join('temp_file/',results[0][1]))
    
    return render_template('view_attachment.html', res=res, results=results)



'''
helper functions to read and write files
'''
def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    flname = 'app/static/'+filename
    with open(flname, 'wb') as f:
        f.write(data)
    
        
#read the file to input to db
def read_file(filename):
    print(filename)
    with open(filename, 'rb') as f:
        dat = f.read()
    return dat






