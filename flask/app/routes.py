from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, session
from app import app
from app.forms import EditForm, RegisterForm, BugReportForm, LoginForm, SearchForm, ExportForm, addFuncAreaForm, addProgramForm
from app.forms import editFuncAreaForm
from flaskext.mysql import MySQL
from functools import wraps
import os, sys, gzip
import base64
from app.user_object import User
import json
mysql = MySQL()


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'system'
app.config['MYSQL_DATABASE_DB'] = 'bughound'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
mysql.init_app(app)

user_ =User('fake',0)

     
@app.route('/')
@app.route('/index')
def index():
    if user_.level == 0:
        return redirect(url_for('login'))
    
    return render_template('index.html', title='Home', user=user_)


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    result= None
    
    form = LoginForm()
    con = mysql.connect()
    cursor = con.cursor()
    
    if request.method == 'POST':
    
        if form.validate_on_submit():
            validate = (
                str(form.username.data), 
                str(form.password.data)
                )
            try:
                sql = "select * from Employee where username=%s and password=%s"
                cursor.execute(sql, validate)
                result = cursor.fetchall()
                
                if len(result) == 1:
                    user_.username=result[0][2]
                    user_.level = result[0][4]
                    
                    return redirect(url_for('index'))
                else:
                    error = 'Username or Password incorrect!'
                
            except Exception as e:
                print(result, file=sys.stderr)
                flash("Problem inserting into db: " + str(e))
                return redirect(url_for('register'))
    return render_template('login.html', error=error, form=form)

    
@app.route('/logout')
def logout():
    user_.username='fake'
    user_.level=0
    return redirect(url_for('login'))


@app.route('/select')
def select():
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    
    cursor = mysql.connect().cursor()
    sql = "select * from Employee"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('db.html', results=results)


#Display links to edit a selected Functional Area
@app.route('/selectFunctionalArea')
def selectFunctionalArea():
    error=None
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    cursor = mysql.connect().cursor()
    sql = "select * from FunctionalArea"

    try:
        cursor.execute(sql)        
        results = cursor.fetchall()
    except Exception as e:
        print(e, file=sys.stderr)        
        flash("Cannot retrieve any functional areas.",error)
        return redirect(url_for('index'))

    sql = "SELECT * FROM Program"
    cursor.execute(sql)
    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"
    programList = [(i[0], (programStr % i[1:4])) for i in programs]  
    programDict = dict(programList)
    functionalAreas = [list(x) for x in results]
    for area in functionalAreas:
        area[2] =  programDict.get(area[2])

    return render_template('dbFunctionalArea.html', results=functionalAreas, user = user_, error=error)


@app.route('/selectProgram')
def selectProgram():
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    cursor = mysql.connect().cursor()
    sql = "select * from Program"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('dbProgram.html', results = results, user=user_)


@app.route('/editBugReport/<id>', methods=['GET', 'POST'])
def editBugReport(id):
    if user_.level ==0:
        return redirect(url_for('login'))
    error = None
    form = BugReportForm()
    con = mysql.connect()
    cursor = con.cursor()

    sql = "SELECT * FROM BugReport WHERE reportId="+str(id)
    cursor.execute(sql)
    report = cursor.fetchone()

    sql = "SELECT * FROM Program"
    cursor.execute(sql)
    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"
    programList = [(i[0], (programStr % i[1:4])) for i in programs]    
    form.program.choices = programList
    
    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)
    employees = cursor.fetchall()
    employeesOptional = ((-1,''),) + employees
    form.reportedBy.choices = employees
    form.assignedTo.choices = employeesOptional
    form.resolvedBy.choices = employeesOptional
    form.testedBy.choices = employeesOptional

    if request.method == 'GET':
        form.program.data = report[1]
        form.reportType.data = report[2]
        form.severity.data = report[3]
        form.reportedBy.data = report[8]
        form.assignedTo.data = report[10]
        form.status.data = report[12]
        form.priority.data = report[13]
        form.resolution.data = report[14]
        form.resolvedBy.data = report[16]
        form.testedBy.data = report[18]
        form.summary.data = report[4]
        form.reproducable.data = (report[5] == 1)
        form.description.data = report[6]
        form.suggestedFix.data = report[7]
        form.discoveredDate.data = report[9]
        form.comments.data = report[11]
        form.resolutionVersion.data = report[15]
        form.resolvedDate.data = report[17]
        form.testedDate.data = report[19]
        form.deferred.data = (report[20] == 1)

    elif request.method == 'POST': 
        if form.validate_on_submit():
            reproducable = int(str(form.reproducable.data) == 'True')
            deferred = int(str(form.deferred.data) == 'True')
            bugReportData = {
                "programId": (form.program.data),
                "reportType": (form.reportType.data),
                "severity": (form.severity.data),
                "summary": str("'" + form.summary.data + "'"),
                "reproducable": (reproducable),
                "description": str("'" + form.description.data + "'"),
                "suggestedFix": str("'" + form.suggestedFix.data + "'"),
                "reportedBy": (form.reportedBy.data),
                "discoveredDate": str("'" + str(form.discoveredDate.data) + "'"),
                "assignedTo": (form.assignedTo.data),
                "comments": str("'" + form.comments.data + "'"),
                "status": (form.status.data),
                "priority": (form.priority.data),
                "resolution": (form.resolution.data),
                "resolutionVersion": (form.resolutionVersion.data),
                "resolvedBy": (form.resolvedBy.data),
                "resolvedDate": str("'" + str(form.resolvedDate.data) + "'"),
                "testedBy": (form.testedBy.data),
                "testedDate": str("'" + str(form.testedDate.data) + "'"),
                "deferred": (deferred)
                }

            invalid = ('', '-1', 'None', "''", "'-1'", "'None'")
            updatedBugReport = { key:val for key, val in bugReportData.items() if val not in invalid}
            reportParams = ''.join('{} = {}, '.format(key, val) for key, val in updatedBugReport.items())            
            try:
                sql = "UPDATE BugReport SET " + reportParams[:-2] + " WHERE reportId=" + str(report[0])
                cursor.execute(sql)
                con.commit()
                flash(f"Bug Report #{report[0]} Updated")
                return redirect(url_for('search'))
            except Exception as e:
                flash("Error: " + str(e))
                return redirect(url_for('editBugReport', id=id))
                
    return render_template('edit_bug_report.html', form=form, error=error, user=user_, id=id)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
 
    form = EditForm()
    con = mysql.connect()
    cursor = con.cursor()

    sql = "SELECT * FROM Employee where employeeId="+str(id)
    cursor.execute(sql)
    results = cursor.fetchone()
    employeeString = results

    if request.method == 'GET':      
        form.name.data = results[1]
        form.username.data = results[2]
        form.password.data = ""
        form.userLevel.data = results[4]
    elif request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('select'))
        if form.validate_on_submit():
            editedEmployee = (
                str(form.name.data), 
                str(form.username.data), 
                str(form.password.data), 
                str(form.userLevel.data)
                )
            try:
                sql = "UPDATE Employee SET name=%s, username=%s, password=%s, level=%s WHERE employeeId="+str(id)
                cursor.execute(sql, editedEmployee)
                con.commit()
                flash('Employee information updated.')
                return redirect(url_for('select'))
            except Exception as e:
                print("Problem editing Employee in db: " + str(e))
                return redirect(url_for('select'))
    
    return render_template('edit.html', results=employeeString, form=form)


@app.route('/editFunctionalArea/<id>', methods =['GET' , 'POST'])
def editFunctionalArea(id):
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))

    error = None
    
    form = editFuncAreaForm()
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM FunctionalArea where areaId="+str(id)
    cursor.execute(sql)
    functionalArea = cursor.fetchone()

    sql = "SELECT * FROM Program"
    cursor.execute(sql)
    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"
    programList = [(i[0], (programStr % i[1:4])) for i in programs]    
    form.program.choices = programList

    if request.method == 'GET':
        form.area.data=functionalArea[1]
        form.program.data=functionalArea[2]

    elif request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('selectFunctionalArea'))
        if form.validate_on_submit():
            functionalAreaData = {
                "areaName": str("'" + form.area.data + "'"),
                "programId": form.program.data
            }
            areaParams = ''.join('{} = {}, '.format(key, val) for key, val in functionalAreaData.items())  
            try:
                sql = "UPDATE FunctionalArea SET " + areaParams[:-2] + " WHERE areaId="+str(id)
                cursor.execute(sql)
                con.commit()
                flash("Functional Area edited")
                return redirect(url_for('selectFunctionalArea'))
            except Exception as e:
                flash("Invalid entry, please try again.", e)
                return redirect(url_for('selectFunctionalArea'))
            
    return render_template('editFunctionalArea.html',error = error, form=form)


@app.route('/editProgram/<id>', methods = ['Get' , 'Post'])
def editProgram(id):
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))

    form = addProgramForm()
    con = mysql.connect()
    cursor = con.cursor()
    
    sql = "SELECT * from Program WHERE programID=" +str(id)
    cursor.execute(sql)
    results = cursor.fetchone()
    programIDString = results
    
    if request.method == 'GET':
        form.name.data=results[1]
        form.version.data=results[2]
        form.releaseNumber.data=results[3]
        form.description.data=results[4]
    elif request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('selectProgram'))
        if form.validate_on_submit():
            editedProgram = (
                             str(form.name.data),
                             str(form.version.data),
                             str(form.releaseNumber.data),
                             str(form.description.data))
            try:
                sql = "UPDATE Program SET name=%s, version=%s, releaseNumber=%s, description=%s where programID=" +str(id)
                cursor.execute(sql, editedProgram)
                con.commit()
                flash("Program Edited.")
                return redirect(url_for('selectProgram'))
            except Exception as e:
                flash("problem" + str(e))
                return redirect(url_for('selectProgram'))
    
    return render_template('editProgram.html', results = programIDString, form = form)
    

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if user_.level == 0:
         return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    
    error = None
    form = RegisterForm(request.form)
    con = mysql.connect()
    cursor = con.cursor()

    if request.method == 'POST':    
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('register'))
        if form.validate_on_submit():
            newEmployee = (
                str(form.name.data), 
                str(form.username.data), 
                str(form.password.data), 
                str(form.userLevel.data), 
                )
            try:
                sql = "INSERT INTO Employee (name, username, password, level) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, newEmployee)
                
                con.commit()
                flash('New Employee Added.')
                return redirect(url_for('register'))
            except Exception as e:
                flash("Problem inserting into db: " + str(e))
                return redirect(url_for('register'))
    return render_template('register.html', form=form, error=error, user=user_)


@app.route('/addFunctionalArea', methods=['GET','POST'])
def addFunctionalArea():
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    add_function_error = None
    error = None
    form = addFuncAreaForm(request.form)
       
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM Program"
    cursor.execute(sql)
    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"
 
    programList = [(0,'')] + [(i[0], (programStr % i[1:4])) for i in programs]    
    form.program.choices = programList
     
    if request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('addFunctionalArea'))
        if form.validate_on_submit():  
            newProgram = (str(form.area.data),
                          str(form.program.data))
            try:
                sql = 'INSERT INTO FunctionalArea(areaName, programId) VALUES (%s, %s)'
                res = cursor.execute(sql, newProgram)
                con.commit()
                flash('New Functional Area Added.')
                return redirect(url_for('addFunctionalArea'))
            except Exception as e:
                print(e, file=sys.stderr)
                error = 'Invalid entry, please try again.'
                
                flash("Cannot add new functional area without program.",add_function_error)
                return redirect(url_for('addFunctionalArea'))
    
    return render_template('addFunctionalArea.html', form=form,error=error, add_function_error=add_function_error)


@app.route('/addProgram', methods=['GET', 'POST'])
def addProgram():
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    error = None
    form = addProgramForm(request.form)
    newProgram= (
                 str(form.name.data),
                 str(form.version.data),
                 str(form.releaseNumber.data),
                 str(form.description.data))
    con = mysql.connect()
    cursor = con.cursor()
    if request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('addProgram'))
        if form.validate_on_submit():
            newProgram= (
                 str(form.name.data),
                 str(form.version.data),
                 str(form.releaseNumber.data),
                 str(form.description.data))
            try:
                sql = 'INSERT INTO Program(name, version, releaseNumber, description) VALUES(%s, %s, %s, %s)'
                cursor.execute(sql,newProgram)
                con.commit()
                flash("New Program Added")
                return redirect(url_for('addProgram'))
            except Exception as e:
                flash("problem inserting into Database: " + str(e))
                return redirect(url_for('addProgram'))
    return render_template('addProgram.html', form=form, error=error)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    if user_.level == 0:
         return redirect(url_for('login'))
    error = None
    form = SearchForm(request.form)
    con = mysql.connect()
    cursor = con.cursor()
    sql = "SELECT * FROM Program"
    cursor.execute(sql)
    programs = cursor.fetchall()
    programStr = "%s, version: %s, release: %s"

    programList = [(-1,'')] + [(i[0], (programStr % i[1:4])) for i in programs]    
    form.program.choices = programList
    
    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)
    employees = ((-1,''),) + cursor.fetchall()
    form.reportedBy.choices = employees
    form.assignedTo.choices = employees
    form.resolvedBy.choices = employees

    sql = "SELECT * FROM FunctionalArea"
    cursor.execute(sql)
    areas = cursor.fetchall()
    areas_list= [('',''),] + [(str(i[0]), str(i[0])) for i in areas]
    form.areaName.choices = areas_list

    if request.method == 'POST':
        if form.validate_on_submit():
            allData = {
                "programId" : str(form.program.data),
                "reportType" : str(form.reportType.data),
                "severity" : str(form.severity.data),
                "assignedTo" : str(form.assignedTo.data),
                "status" : str(form.status.data),
                "priority" : str(form.priority.data),
                "resolution" : str(form.resolution.data),
                "reportedBy" : str(form.reportedBy.data),
                "discoveredDate" : str(form.discoveredDate.data),
                "resolvedBy" : str(form.resolvedBy.data)
            }
            invalid = ('', '-1', 'None')
            searchData = { key:val for key, val in allData.items() if val not in invalid}
            queryParams = ''.join('{} = {} AND '.format(key, val) for key, val in searchData.items())
            sql = "SELECT reportId, programId, summary FROM BugReport" + (" WHERE " if queryParams else '') + queryParams[:-5]


            cursor.execute(sql)
            programDict = dict(programList)
            reports = cursor.fetchall()

            if not reports:
                flash("No bug reports match your search", 'warning')
            else:
                changedReports = []
                for result in reports:
                    changedResult = list(result)
                    changedResult[1] = programDict.get(result[1])
                    changedReports.append(changedResult)

                session['searchResults'] = changedReports
                return render_template('dbBugReport.html')

    return render_template('search.html', form=form, error=error, user=user_)


@app.route('/bug_report/', methods=['GET', 'POST'])
def bug_report():
    if user_.level == 0:
        return redirect(url_for('login'))
    
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
    employeesOptional = ((-1,''),) + employees
    form.assignedTo.choices = employeesOptional
    form.resolvedBy.choices = employeesOptional
    form.testedBy.choices = employeesOptional

    if request.method == 'POST':
        if 'cancel' == request.form.get('cancel'):
            return redirect(url_for('bug_report'))
        if form.validate_on_submit():
            reproducable = int(str(form.reproducable.data) == 'True')
            deferred = int(str(form.deferred.data) == 'True')
            bugReportData = [
                'None',
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
                ]

            invalid = ('', '-1', 'None')
            bugReportData = ["'" + i + "'" if i not in invalid else 'DEFAULT' for i in bugReportData]
            
            reportString = ''.join("{}, ".format(val) for val in bugReportData)
            reportString = reportString[:-2]
            try:
                sql = "INSERT INTO BugReport VALUES (" + reportString + ")"
                cursor.execute(sql)
                con.commit()

                flash('New Bug Report added')

                return redirect(url_for('bug_report'))
            except Exception as e:
                flash("Problem inserting into db: " + str(e))
                return redirect(url_for('bug_report'))

    return render_template('bug_report.html', form=form, error=error, user=user_)


@app.route('/upload')
def upload_file():
    if user_.level == 0:
        return redirect(url_for('login'))
    
    return render_template('upload.html')


@app.route('/uploader/<report>', methods=['GET', 'POST'])
def upload(report):
    #error = None
    if user_.level == 0:
        return redirect(url_for('login'))
   
    if request.method == 'POST':
        f = request.files['inputFile']
        f.save(os.path.join('temp_file/',f.filename))
        
        con = mysql.connect()
        cursor = con.cursor() 

        newUpload = (
                    str(report),
                    str(f.filename), 
                    read_file(os.path.join('temp_file/',f.filename))
                    )
                    
        sql = "INSERT INTO Attachment (reportId, fileName, file) VALUES (%s, %s, %s)"
        
        try:
            cursor.execute(sql, newUpload)
            con.commit()
            
            flash(f'New attachment added to Bug Report #{report}.')
            return redirect(url_for('upload', report=report))

        except Exception as e:
            flash("Problem inserting into db: " + str(e))
            os.remove(os.path.join('temp_file/',f.filename))
            con.close()
            return redirect(url_for('upload', report=report))

        #clean file
        os.remove(os.path.join('temp_file/',f.filename))
        con.close()  
        return redirect(url_for('index'))          
  
    return render_template('upload.html', user=user_)


'''
Select all from the attachment table and place
results in a table in attachments.html.
'''
@app.route('/attachments')
def attachments():
    if user_.level == 0:
        return redirect(url_for('login'))
    cursor = mysql.connect().cursor()
    sql = "select * from Attachment"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        flash("Problem getting files: " + str(e))
    return render_template('attachments.html', results=results, user=user_)


'''
When a file gets selected in attachments.html
the <report> number and the <file> name are passed here.
Then, this function selects that specific file and
renders it in view_attachment.html.
'''
@app.route('/showFile/<report>/<file>')
def showFile(report,file):
    if user_.level == 0:
        return redirect(url_for('login'))
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
        res.append(results[0][1])
    else:
        path = 'app/static/'+file_
        text = open(path, 'r+')
        res.append(text.read())
        text.close()    
    return render_template('view_attachment.html', res=res, results=results, user=user_)


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


@app.route('/export/', methods=['GET', 'POST'])
def export():
    if user_.level == 0:
        return redirect(url_for('login'))
    
    error = None
    form = ExportForm(request.form)
    
    if request.method == 'POST':
        con = mysql.connect()
        cursor = con.cursor()
        tables = []
        if form.bugReport.data:
            sql = "SELECT * FROM BugReport"
            cursor.execute(sql)
            bugReportTable = cursor.fetchall()
            tables.append(bugReportTable)

        if form.employee.data:
            sql = "SELECT * FROM Employee"
            cursor.execute(sql)
            employeeTable = cursor.fetchall()
            tables.append(employeeTable)

        if form.functionalArea.data:
            sql = "SELECT * FROM FunctionalArea"
            cursor.execute(sql)
            functionalAreaTable = cursor.fetchall()
            tables.append(functionalAreaTable)

        if form.program.data:
            sql = "SELECT * FROM Program"
            cursor.execute(sql)
            programTable = cursor.fetchall()
            tables.append(programTable)

        if form.attachment.data:
            sql = "SELECT reportID, fileName From Attachment"
            cursor.execute(sql)
            attachmentTable = cursor.fetchall()
            tables.append(attachmentTable)

        if not tables:
            flash("No tables selected")
        else:
            tablesJSON = jsonify(tables)
            tablesJSON.headers['Content-Disposition'] = 'attachment;filename=tables.json'
            return tablesJSON

    return render_template('export.html', form=form, error=error, user=user_)