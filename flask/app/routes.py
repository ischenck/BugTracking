from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, session
from app import app
from app.forms import EditForm, RegisterForm, BugReportForm, LoginForm, SearchForm

from flaskext.mysql import MySQL
from functools import wraps
import os, sys
import base64
from app.user_object import User

#from utils import *
mysql = MySQL()


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'system'
app.config['MYSQL_DATABASE_DB'] = 'bughound'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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
                
                print(len(result), file=sys.stderr)
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
    
#    conn = mysql.connect()
    cursor = mysql.connect().cursor()
    sql = "select * from Employee"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('db.html', results=results)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if user_.level == 0:
        return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    
    
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
    if user_.level == 0:
         return redirect(url_for('login'))
    if user_.level != 2:
         return redirect(url_for('index'))
    
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

    return render_template('register.html', form=form, error=error, user=user_)






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

    programList = [(0,'')] + [(i[0], (programStr % i[1:4])) for i in programs]    
    form.program.choices = programList
    
    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)

    employees = ((0,''),) + cursor.fetchall()

    form.reportedBy.choices = employees
    form.assignedTo.choices = employees
    form.resolvedBy.choices = employees

    sql = "SELECT * FROM FunctionalArea"
    cursor.execute(sql)
    areas = cursor.fetchall()
    areas_list= [('',''),] + [(str(i[0]), str(i[0])) for i in areas]
    form.areaName.choices = areas_list

    sql = "SELECT reportId, fileName FROM Attachment"
    cursor.execute(sql)
    attachments = cursor.fetchall()
    print(attachments)
    if request.method == 'POST':
        if form.validate_on_submit():
            allData = {
                "programId" : str(form.program.data),
                "reportType" : str(form.reportType.data),
                "severity" : str(form.severity.data),
                "areaName" : str(form.areaName.data),
                "assignedTo" : str(form.assignedTo.data),
                "status" : str(form.status.data),
                "priority" : str(form.priority.data),
                "resolution" : str(form.resolution.data),
                "reportedBy" : str(form.reportedBy.data),
                "discoveredDate" : str(form.discoveredDate.data),
                "resolvedBy" : str(form.resolvedBy.data)
            }
            invalid = ('', '0', 'None')
            searchData = { key:val for key, val in allData.items() if val not in invalid}
            queryParams = ''.join('{} = {} AND '.format(key, val) for key, val in searchData.items())
            sql = "SELECT * FROM BugReport" + (" WHERE " if queryParams else '') + queryParams[:-5]
            
            reportTypeDict = {
                0: '', 
                1: "Coding Error",
                2: "Suggestions",
                3: "Documentation",
                4: "Hardware",
                5: "Query" 
            }
            severityDict = {
                0: '',
                1: 'Fatal',
                2: 'Serious',
                3: 'Minor'
            }
            priorityDict = {
                0: '',
                1: "Fix immediately", 
                2: "Fix as soon as possible", 
                3: "Fix before next milestone",
                4: "Fix before release", 
                5: "Fix if possible)", 
                6: "Optional"
            }
            resolutionDict = {
                0: '', 
                1: "Pending",
                2: "Fixed",
                3: "Irreproducible", 
                4: "Deferred", 
                5: "As designed",
                6: "Withdrawn by reporter", 
                7: "Need more info",
                8: "Disagree with suggestion",
                9: "Duplicate"
            }
            programDict = dict(programList)
            employeesDict = dict(employees)
            attachmentsDict = dict(attachments)

            cursor.execute(sql)

            reports = cursor.fetchall()
            printableReports = []
            for i in range(len(reports)):
                printableReports.append({
                    "Program": programDict.get(reports[i][1]),
                    "Report Type": reportTypeDict.get(reports[i][2]),
                    "Severity": severityDict.get(reports[i][3]),
                    "Summary": reports[i][4],
                    "Reproducable": "Yes" if reports[i][5] == 1 else "No",
                    "Description": reports[i][6],
                    "Suggested Fix": reports[i][7],
                    "Reported By": employeesDict.get(reports[i][8]),
                    "Discovered Date": reports[i][9],
                    "Assigned To": employeesDict.get(reports[i][10]),
                    "Comments": reports[i][11],
                    "Status": "Open" if reports[i][12] == 1 else "Closed",
                    "Priority": priorityDict.get(reports[i][13]),
                    "Resolution": resolutionDict.get(reports[i][14]),
                    "Resolution Version": reports[i][15],
                    "Resolved By": employeesDict.get(reports[i][16]),
                    "Resolved Date": reports[i][17],
                    "Tested By": employeesDict.get(reports[i][18]),
                    "Test Date": reports[i][19],
                    "Deferred": "Yes" if reports[i][20] == 1 else "No",
                    "Functional Area": reports[i][21],
                    "Attachment": attachmentsDict.get(reports[i][0], 'None')
                })

            reportsResult = []
            for i in range(len(printableReports)):
                reportsResult.append(''.join("{}: {} \n".format(key, val) for key, val in printableReports[i].items()))

            session['reports'] = reportsResult
            return redirect(url_for('results'))

    return render_template('search.html', form=form, error=error, user=user_)

@app.route('/results/')
def results():
    return render_template("results.html")

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

    #get funtional area and pass to select list
#    sql = "SELECT areaName FROM FunctionalArea"
#    cursor.execute(sql)
#    funcAreaList=[]
#    for i,j in enumerate(cursor.fetchall()):
#        funcAreaList.append((i,str(j[0])))
#    form.areaName.choices = funcAreaList
    #end functionalArea
   
    sql = "SELECT * FROM FunctionalArea"
    cursor.execute(sql)
    areas = cursor.fetchall()
    areas_list=[(str(i[0]), str(i[0])) for i in areas]
    form.areaName.choices = areas_list
    
    sql = "SELECT employeeId, name FROM Employee"
    cursor.execute(sql)

    employees = cursor.fetchall()

    form.reportedBy.choices = employees
    form.assignedTo.choices = employees
    form.resolvedBy.choices = employees
    form.testedBy.choices = employees

    #sql = "SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'bughound' AND TABLE_NAME = 'BugReport'"
    #cursor.execute(sql)
    #id = cursor.fetchone()[0]
    #print(id)

    #if  request.method == 'GET':
    #   return render_template('bug_report.html', form=form, error=error)
    if request.method == 'POST':
        if form.validate_on_submit():
            print("good!")
            #f = form.attachment.data
            #f.save(os.path.join(app.instance_path, 'temp_file/', f.filename))

            #attachment = (
            #        str(id),
            #        str(f.filename), 
            #        read_file(os.path.join('temp_file/',f.filename))
            #        )

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
                str(deferred),
                str(form.areaName.data)
                )
            try:
                sql = "INSERT INTO BugReport (programId, reportType, severity, summary, \
                    reproducable, description, suggestedFix, reportedBy, discoveredDate, \
                    assignedTo, comments, status, priority, resolution, \
                    resolutionVersion, resolvedBy, resolvedDate, testedBy, testedDate, \
                    deferred,areaName) \
                    VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                cursor.execute(sql, bugReportData)
                con.commit()
                #sql = "INSERT INTO Attachment (reportId, fileName, file) VALUES (%s, %s, %s)"
                #cursor.execute(sql, attachment)
                #con.commit()
                print('New Bug Report added')

                return redirect(url_for('upload'))
            except Exception as e:
                print("Problem inserting into db: " + str(e))
                #os.remove(os.path.join('temp_file/',f.filename))
                return redirect(url_for('bug_report'))
                
                #clean file
            #os.remove(os.path.join('temp_file/',f.filename))
            #con.close()  
        else:
            print("bad!")
    return render_template('bug_report.html', form=form, error=error, user=user_)

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
    if user_.level == 0:
        return redirect(url_for('login'))
    
    return render_template('upload.html')


@app.route('/uploader/', methods=['GET', 'POST'])
def upload():
    #error = None
    if user_.level == 0:
        return redirect(url_for('login'))
   
    if request.method == 'POST':
        f = request.files['inputFile']
        f.save(os.path.join('temp_file/',f.filename))
        
        con = mysql.connect()
        cursor = con.cursor() 
        sql = "SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'bughound' AND TABLE_NAME = 'BugReport'"
        cursor.execute(sql)
        id = cursor.fetchone()[0] - 1
        print(id)    
        newUpload = (
                    str(id),
                    str(f.filename), 
                    read_file(os.path.join('temp_file/',f.filename))
                    )
                    
        sql = "INSERT INTO Attachment (reportId, fileName, file) VALUES (%s, %s, %s)"
        
        try:
            cursor.execute(sql, newUpload)
            con.commit()
            
            print('New attachment added.')
            return redirect(url_for('bug_report'))

        except Exception as e:
            print("Problem inserting into db: " + str(e))
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






