import datetime
from flask import Flask, flash, render_template, request, redirect, url_for, session, escape
from pymongo import MongoClient
from functools import wraps
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = 'secret'


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
            #mongo adding user stuff:
            if (len(username)<3 or len(password)<3):
                return render_template("signup.html",message="Please fill in required elements. Each required element must have at least 3 characters.")
            elif(password == password2):
                if adduser(username,password,name):
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
    return render_template("welcome.html", name=getname(session['myuser']), TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/todo")
def todo():
    return render_template("todo.html", homeworks = homeworks.find({"assignedTo": session['myuser'], "status": "in progress"}), TDnum = getTDnum(), MYHWnum = getMYHWnum() )

@app.route("/profile", methods=["GET","POST"])
@authenticate("/profile")
def profile():
    return render_template("profile.html", name = getname(session['myuser']),
                           username = session['myuser'], TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/addhw", methods=["GET","POST"])
@authenticate("/addhw")
def addhw():
    message = ""
    if request.method=="GET":
        return render_template("addhw.html", message=message, TDnum = getTDnum(), MYHWnum = getMYHWnum())
    else:
        if request.form['b']=="Submit":
            subject = request.form['r']
            title = request.form['title']
            description = request.form['description']
            content = request.form['content']
            due = request.form['due']
            #tags = request.form['tags']
            addhomework(subject,title,description,content,due)
            return render_template("addhw.html", message="Homework successfully posted.", TDnum = getTDnum(), MYHWnum = getMYHWnum())
        else:
            return render_template("welcome.html", TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/myhw")
@authenticate("/myhw")
def myhw():
    return render_template("myhw.html",
                           incomplete = homeworks.find({"poster":session['myuser'] , "status": "incomplete"}),
                           inprogress = homeworks.find({"poster":session['myuser'] , "status":"in progress"}),
                           completed  = homeworks.find({"poster":session['myuser']  , "status": "complete"}),
                           TDnum = getTDnum(),
                           MYHWnum = getMYHWnum(),
                           )

@app.route("/myrecs")
@authenticate("/myrecs")
def myrecs():
    return render_template("myrecs.html",homeworks = homeworks.find(), user=session['myuser'], TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/viewhw/<idnum>", methods=["GET", "POST"])
#@authenticate("/viewhw/<idnum>")
def viewhw(idnum):
    homework = homeworks.find_one({"_id":ObjectId(idnum)})
    if request.method=="GET":
        return render_template("viewhw.html", homework = homework, user = session['myuser'], TDnum = getTDnum(), MYHWnum = getMYHWnum())
    elif request.form['b']=="Claim":
        homework['status'] = "in progress"
        homework['assignedTo'] = session['myuser']
        homeworks.save(homework)
        return redirect(url_for("todo"))
    elif request.form['b'] == "Submit":
        homework['help'] = request.form['help']
        homework['status'] = "complete"
        homeworks.save(homework)
        return redirect(url_for("todo"))



@app.route("/search", methods=["GET","POST"])
@authenticate("/search")
def search():
    if request.method=="GET":
        return render_template("search.html", TDnum = getTDnum(), MYHWnum = getMYHWnum())
    else:
        if request.form['b']=="Search":
            query = request.form['query']
            #searching stuff!!
            return render_template("search.html",message=query, TDnum = getTDnum(), MYHWnum = getMYHWnum())
        else:
            return render_template("welcome.html", TDnum = getTDnum(), MYHWnum = getMYHWnum() )


def getname(uname):
    users = db.info.find()
    for user in users:
        if user['user'] == uname:
            return user['name']

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

def adduser(uname,pword, name):
    if db.info.find_one({'user':uname}) == None:
        d = {'user':uname,'pass':pword, 'name':name}
        db.info.insert(d)
        return True
    return False

#adds homework to database (WIP):
def addhomework(subject,title,desc,work,due):
    homework = {"subject":subject,
            "title":title,
            "description":desc,
            "work":work,
            "date":datetime.datetime.utcnow(),
            "due": due,
            "poster":session['myuser'],
            "status": "incomplete",
            "assignedTo": None,
            "help": None}
    post_id = homeworks.insert(homework)
#for testing purposes, prints homeworks in terminal:
#for homework in homeworks.find():
#   print(homework)

def getTDnum():
    return homeworks.find({"assignedTo":session['myuser'], "status": "in progress"}).count()

def getMYHWnum():
    return homeworks.find( {"poster": session['myuser'],  "status" : { "$in": ["in progress", "incomplete"] } } ).count()


if __name__=="__main__":
    client = MongoClient()
    db = client['1258']
    #homework collection in database (WIP):
    homeworks = db['homeworks']
    app.debug=True
    app.run()


