from flask import Flask, flash, render_template, request, redirect, url_for, session, escape
from pymongo import MongoClient
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret'

def authenticate(page):
    def decorate(f):
        @wraps(f)
        def inner(*args):
            if 'user' not in session:
                flash("You need to be logged in to see that!")
                session['nextpage'] = page
                return redirect(url_for("login.html"))
            return f(*args)
        return inner
    return decorate

@app.route("/home")
@app.route("/")
def home():
    if 'user' in session:
        return redirect(url_for("welcome.html"))
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    message = ""
    if request.method=="GET":
        return render_template("login.html", message=message)
    else:
        if request.form['b']=="About":
            return render_template("login.html", message=message)
        if request.form['b']=="Log In":
            username = request.form["logusername"]
            password = request.form["logpassword"]
            #mongo authentication stuff:
            valid_user = authenticate(username,password)
            if not(valid_user) and not(username==None):
                return render_template("login.html",message="Not a valid user.")
            else:
                session['myuser']=username
                return redirect(url_for('welcome'))
        if request.form['b']=="Sign Up":
            return redirect(url_for('signup'))

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
                if adduser(username,password):
                    return redirect(url_for('login', message="You have registered successfully"))
                else:
                    return render_template("signup.html", message="Username taken. Try Again.")
            else:
                return render_template("signup.html", message="Password doesn't match confirmation.")
        if request.form['b']=="Cancel":
            return redirect(url_for('login'))

@app.route("/welcome",methods=["GET","POST"])
@authenticate("/welcome")
def welcome():
    if request.method=="GET":
        return render_template("welcome.html")
    else:
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/profile", methods=["GET","POST"])
@authenticate("/profile")
def profile():
    if request.method=="GET":
        return render_template("profile.html")
    else:
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        else:
            #there will be other buttons here
            return render_template("welcome.html")

@app.route("/addhw", methods=["GET","POST"])
@authenticate("/addhw")
def addhw():
    message = ""
    if request.method=="GET":
        return render_template("addhw.html", message=message)
    else:
        if request.form['b']=="Submit":
            subject = request.form['r']
            title = request.form['title']
            description = request.form['description']
            summary = request.form['summary']
            content = request.form['content']
            return render_template("addhw.html", message="Homework successfully posted.")
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/myhw", methods=["GET","POST"])
@authenticate("/myhw")
def myhw():
    if request.method=="GET":
        return render_template("myhw.html")
    else:
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/myrecs", methods=["GET","POST"])
@authenticate("/myrecs")
def myrecs():
    if request.method=="GET":
        return render_template("myrecs.html")
    else:
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/search", methods=["GET","POST"])
@authenticate("/search")
def search():
    if request.method=="GET":
        return render_template("search.html")
    else:
        if request.form['b']=="Search":
            query = request.form['query']
            #searching stuff!!
            return render_template("search.html",message=query)
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")


def getpword(uname):
    names = db.info.find()
    for name in names:
        if name['user'] == uname:
            return name['pass']

def authenticate(uname,pword):
    names = db.info.find()
    for name in names:
        if name['user'] == uname:
            if name['pass'] == pword:
                return True
    return False

def adduser(uname,pword):
    if db.info.find_one({'user':uname}) == None:
        d = {'user':uname,'pass':pword}
        db.info.insert(d)
        return True
    return False

#def addhomework(subject,title,desc,summary,work):
    #adding a homework to the database

if __name__=="__main__":
    client = MongoClient()
    db = client['1258']
    app.debug=True
    app.run()
        
