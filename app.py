from datetime import datetime
import math
from flask import Flask, flash, render_template, request, redirect, url_for, session, escape
from pymongo import MongoClient
from functools import wraps
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'


def authenticate(page):
    def decorate(f):
        @wraps(f)
        def inner(*args):
            if 'myuser' not in session:
                flash("You need to be logged in to see that!")
                session['nextpage'] = page
                return redirect(url_for("login"))
            return f(*args)
        return inner
    return decorate

@app.route("/home")
@app.route("/")
def home():
    if 'user' in session:
        return redirect(url_for("welcome"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    message = ""
    if request.method=="GET":
        return render_template("login.html", message=message)
    else:
        if request.form['b']=="About":
            return render_template("login.html", message=message)
        if request.form['b']=="Cancel":
            return redirect(url_for('login'))
        if request.form['b']=="Log In":
            username = request.form["logusername"]
            password = request.form["logpassword"]
            #mongo authentication stuff:
            valid_user = authenticate(username,password)
            if not(valid_user) and not(username==None):
                return render_template("login.html",message="Not a valid user.")
            else:
                session['myuser']=username
                return redirect('welcome')
        if request.form['b']=="Sign Up":
            return redirect(url_for('signup'))

@app.route("/logout")
def logout():
    session.pop("myuser", None)
    #print(session)
    return redirect(url_for('login'))

@app.route("/signup", methods=["GET","POST"])
def signup():
    message = ""
    if request.method=="GET":
        return render_template("signup.html", message=message)
    else:
        if request.form['b']=="Sign Up":
            username = request.form["signusername"]
            password = request.form["signpassword"]
            password2 = request.form["signpassword2"]
            name = request.form["name"]
            bio = request.form["bio"]
            #mongo adding user stuff:
            if (len(username)<3 or len(password)<3):
                return render_template("signup.html",message="Please fill in required elements. Each required element must have at least 3 characters.")
            elif(password == password2):
                if adduser(username,password,name,bio):
                    return redirect(url_for('login'))
                else:
                    return render_template("signup.html", message="Username taken. Try Again.")
            else:
                return render_template("signup.html", message="Password doesn't match confirmation.")
        if request.form['b']=="Cancel":
            return redirect(url_for('login'))

@app.route("/welcome")
@authenticate("/welcome")
def welcome():
    checkDates(db.info.find_one({'user': session['myuser']}))
    return render_template("welcome.html", name=db.info.find_one({'user':session['myuser']})['name'], TDnum = getTDnum(), MYHWnum = getMYHWnum())

def checkDates(user):
    #print"\n\n\ncheckdates method"
    user = db.info.find_one({'user':session['myuser']})
    #print "USER:"
    #print(user)
    todos = homeworks.find({"assignedTo":user['user']})
    #print "TODOS:"
    #print(todos)
    for hw in todos:
        if overdue(hw['due']):
            user['incomplete'] = user['incomplete'] + 1;
            hw['status'] = "incomplete"
            hw['assignedTo'] = None
            db.info.save(user)
            homeworks.save(hw)

def overdue(due):
    duedate = datetime(int(due[:4]), int(due[5:7]), int(due[8:10])).date()
    if duedate < datetime.today().date():
    #if duedate < datetime(2016, 12, 12).date():
        return True
    return False




@app.route("/todo")
def todo():
    checkDates(db.info.find_one({'user':session['myuser']}))
    return render_template("todo.html", homeworks = homeworks.find({"assignedTo": session['myuser'], "status": "in progress"}), TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/profile", methods=["GET","POST"])
@authenticate("/profile")
def profile():
    user = db.info.find_one({'user':session['myuser']})
    incompletes = user['incomplete']
    completes = user['completed']
    if incompletes == 0 or completes == 0:
        rating = 100
    else:
        rating = int(((completes + 0.0) / (incompletes + completes)) * 100)
    if request.method=="GET":
        return render_template("profile.html",
                               name = getname(session['myuser']),
                               username = session['myuser'],
                               bio = getbio(session['myuser']),
                               points = getpoints(session['myuser']),
                               user = user,
                               rating = rating,
                               MYHWnum = getMYHWnum(),
                               TDnum = getTDnum())


@app.route("/addhw", methods=["GET","POST"])
@authenticate("/addhw")
def addhw():
    message = ""
    if request.method=="GET":
        return render_template("addhw.html", message=message, TDnum = getTDnum(), MYHWnum = getMYHWnum())
    else:
        if request.form['b']=="Submit":
            due = request.form['due']
            subject = request.form['r']
            title = request.form['title']
            description = request.form['description']
            work = request.form['work']
            tags = request.form['tags']
            if ((not checkDate(due)) or title == "" or description == "" or work == "" or due == ""):
                return render_template("addhw.html", message = "Please fill in all fields correctly.", TDnum=getTDnum(), MYHWnum=getTDnum())
            addhomework(subject,title,description,work,due,tags)
            return render_template("addhw.html", message="Homework successfully posted.", TDnum = getTDnum(), MYHWnum = getMYHWnum())

def checkDate(due):
    try:
        newDate = datetime(int(due[:4]), int(due[5:7]), int(due[8:10])).date()
        #print "\n\n\n"
        #print newDate
        if newDate > datetime.today().date():
            result = True
        else:
            result = False
    except:
        result = False
    #print result
    return result


@app.route("/myhw")
@authenticate("/myhw")
def myhw():
    progress = homeworks.find({"poster":session['myuser'], "status": "in progress"})
    #print progress
    for hw in progress:
        checkDates(hw['assignedTo'])
    return render_template("myhw.html",
                           incomplete = homeworks.find({"poster":session['myuser'] , "status": "incomplete"}),
                           inprogress = homeworks.find({"poster":session['myuser'] , "status":"in progress"}),
                           completed  = homeworks.find({"poster":session['myuser']  , "status": "complete"}),
                           TDnum = getTDnum(),
                           MYHWnum = getMYHWnum(),
                           )

@app.route("/browse")
@authenticate("/browse")
def browse():
    return render_template("browse.html",
                           homeworks = homeworks.find(),
                           TDnum = getTDnum(),
                           MYHWnum = getMYHWnum(),
                       )
@app.route("/myrecs")
@authenticate("/myrecs")
def myrecs():
    recs = []
    for hw in homeworks.find():
        if (not overdue(hw['due'])) and (hw['poster'] != session['myuser']) and (hw['status'] == "incomplete"):
            recs.append(hw)
    return render_template("myrecs.html",
                           homeworks = recs,
                           user=session['myuser'],
                           TDnum = getTDnum(),
                           MYHWnum = getMYHWnum())

@app.route("/viewhw/<idnum>", methods=["GET", "POST"])
#@authenticate("/viewhw/<idnum>")
def viewhw(idnum):
    homework = homeworks.find_one({"_id":ObjectId(idnum)})
    if request.method=="GET":
        return render_template("viewhw.html",
                               homework = homework,
                               user = session['myuser'],
                               TDnum = getTDnum(),
                               MYHWnum = getMYHWnum())
    elif request.form['b']=="Claim":
        homework = homeworks.find_one({"_id":ObjectId(idnum)})
        homework['status'] = "in progress"
        homework['assignedTo'] = session['myuser']
        homeworks.save(homework)
        return redirect(url_for("todo"))
    elif request.form['b'] == "Submit":
        homework['help'] = request.form['help']
        homework['status'] = "complete"
        homeworks.save(homework)
        user = db.info.find_one({'user':session['myuser']})
        user['completed'] = user['completed'] + 1
        db.info.save(user)
        return redirect(url_for("todo"))

@app.route("/delete/<idnum>")
#@authenticate("/delete/<idnum>")
def delete(idnum):
    homeworks.remove( {"_id": ObjectId(idnum)});
    return redirect(url_for("myhw"))

@app.route("/claim/<idnum>")
#@authenticate("/claim/<idnum>")
def claim(idnum):
    homework = homeworks.find_one({"_id":ObjectId(idnum)})
    homework['status'] = "in progress"
    homework['assignedTo'] = session['myuser']
    homeworks.save(homework)
    return redirect(url_for("todo"))


@app.route("/search", methods=["GET","POST"])
@authenticate("/search")
def search():
    message=""
    subjects = [["English","book"],["History","globe"],["Math","stats"],["Science","leaf"]]
    if request.method=="GET":
        return render_template("search.html",subjects=subjects, TDnum = getTDnum(), MYHWnum = getMYHWnum())
    else:
        query = request.form['query'].lower()
        subject = request.form['subject']
        if (query != ""):
            results = homeworks.find({'tags_array': query, 'poster': {'$ne': session['myuser']}, 'status': 'incomplete' })
        else:
            results = homeworks.find({'subject': subject, 'poster': {'$ne': session['myuser']}, 'status': 'incomplete' })
        finalresults = []
        for hw in finalresults:
            if (not overdue(hw['due'])) and (hw['poster'] != session['myuser']) and (hw['status'] == "incomplete"):
                finalresults.append(hw)
        return render_template("search.html",
                               message= str(results.count()) + " result(s) found",
                               results=results, subject=subject, subjects=subjects, user = session['myuser'],
                               TDnum = getTDnum(),
                               MYHWnum = getMYHWnum())

def getname(uname):
    users = db.info.find()
    for user in users:
        if user['user'] == uname:
            return user['name']

def getbio(uname):
    users = db.info.find()
    for user in users:
        if user['user'] == uname:
            return user['bio']

def getpoints(uname):
    users = db.info.find()
    for user in users:
        if user['user'] == uname:
            return user['points']

def getpword(uname):
    names = db.info.find()
    for name in names:
        if name['user'] == uname:
            return name['pass']

def authenticate(uname,pword):
    names = db.info.find()
    for name in names:
        #print name
        if name['user'] == uname:
            if name['pass'] == pword:
                return True
    return False

def adduser(uname,pword,name,bio):
    if db.info.find_one({'user':uname}) == None:
        d = {'user':uname,'pass':pword, 'name':name, 'bio':bio, 'points':0, 'completed': 0, 'incomplete': 0}
        db.info.insert(d)
        return True
    return False

#adds homework to database (WIP):
def addhomework(subject,title,desc,work,due,tags):
    homework = {"subject":subject,
            "title":title,
            "description":desc,
            "work":work,
            "date": str(datetime.today().date()),
            "due": due,
            "poster":session['myuser'],
            "tags_string":tags.lower(),
            "tags_array":tags.lower().split(", "),
            "status": "incomplete",
            "assignedTo": None,
            "help": None}
    post_id = homeworks.insert(homework)
#for testing purposes, prints homeworks in terminal:
#for homework in homeworks.find():
#print(homework)

def getTDnum():
    return homeworks.find({"assignedTo":session['myuser'], "status": "in progress"}).count()

def getMYHWnum():
    return homeworks.find( {"poster": session['myuser'],  "status" : { "$in": ["in progress", "incomplete"] } } ).count()



if __name__=="__main__":
    client = MongoClient()
    db = client['1258']
    homeworks = db['homeworks']
    info = db['info']
    app.debug=True
    app.secret_key = 'secret'
    app.run()
