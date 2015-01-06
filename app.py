from flask import Flask, flash, render_template, request, redirect, url_for, session, escape
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'secret'

@app.route("/", methods=["GET","POST"])
def home():
    message = ""
    if request.method=="GET":
        return render_template("home.html", message=message)
    else:
        if request.form['b']=="About":
            return render_template("home.html", message=message)
        if request.form['b']=="Log In":
            username = request.form["logusername"]
            password = request.form["logpassword"]
            #mongo authentication stuff:
            valid_user = authenticate(username,password)
            if not(valid_user) and not(username==None):
                return render_template("home.html",message="Not a valid user.")
            else:
                session['myuser']=username
                return redirect(url_for('welcome'))
        if request.form['b']=="Sign Up":
            username = request.form["signusername"]
            password = request.form["signpassword"]
            password2 = request.form["signpassword2"]
            name = request.form["name"]
            #mongo adding user stuff:
            if (len(username)<3 or len(password)<3):
                return render_template("home.html",message="Please fill in required elements. Each required element must have at least 3 characters.")
            elif(password == password2):
                if adduser(username,password):
                    return render_template("home.html", message="You have successfully registered.")
                else:
                    return render_template("home.html", message="Username taken. Try Again.")
            else:
                return render_template("home.html", message = "Password doesn't match confirmation.")
        if request.form['b']=="Cancel":
            return render_template("home.html", message=message)

@app.route("/welcome",methods=["GET","POST"])
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
def profile():
    if request.method=="GET":
        return render_template("profile.html")
    else:
         if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/addhw", methods=["GET","POST"])
def addhw():
    if request.method=="GET":
        return render_template("addhw.html")
    else:
        if request.form['b']=="Log Out":
            session.pop("myuser", None)
            return redirect(url_for('home'))
        #there will be other buttons here
        else:
            return render_template("welcome.html")

@app.route("/myhw", methods=["GET","POST"])
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
def search():
    if request.method=="GET":
        return render_template("search.html")
    else:
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

if __name__=="__main__":
    client = MongoClient()
    db = client['1258']
    app.debug=True
    app.run()
        
