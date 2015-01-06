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
<<<<<<< HEAD
            #this is where all the authentication mongo stuff would go 
            return redirect(url_for('welcome'))
=======
            #mongo authentication stuff:
            valid_user = authenticate(username,password)
            if not(valid_user) and not(username==None):
                return render_template("home.html",message="Not a valid user.")
            else:
                session['myuser']=username
                return redirect(url_for('welcome'))
>>>>>>> bb4b0370706378117ac20f49039e88d87bef92ed
        if request.form['b']=="Sign Up":
            username = request.form["signusername"]
            password = request.form["signpassword"]
            password2 = request.form["signpassword2"]
            name = request.form["name"]
<<<<<<< HEAD
            #this is where all the adding user mongo stuff would go 
            message = "Registration Sucessful! Log In to get started." 
            return render_template("home.html", message=message)
        if request.form['b']=="Cancel":
            return render_template("home.html", message=message)
    
@app.route("/welcome", methods=["GET","POST"])
=======
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
>>>>>>> bb4b0370706378117ac20f49039e88d87bef92ed
def welcome():
    if request.method=="GET":
        return render_template("welcome.html")
    else:
        return render_template("welcome.html")
        #there will be other buttons here

@app.route("/profile", methods=["GET","POST"])
def profile():
    if request.method=="GET":
        return render_template("profile.html")
    else:
         return render_template("welcome.html")
        #there will be other buttons here

@app.route("/addhw", methods=["GET","POST"])
def addhw():
    if request.method=="GET":
        return render_template("addhw.html")
    else:
        return render_template("welcome.html")
        #there will be other buttons here

@app.route("/myhw", methods=["GET","POST"])
def myhw():
    if request.method=="GET":
        return render_template("myhw.html")
    else:
        return render_template("welcome.html")
        #there will be other buttons here

@app.route("/myrecs", methods=["GET","POST"])
def myrecs():
    if request.method=="GET":
        return render_template("myrecs.html")
    else:
        return render_template("welcome.html")
        #there will be other buttons here

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method=="GET":
        return render_template("search.html")
    if request.form['b']=="Log Out":
        session.pop("myuser", None)
        return redirect(url_for('home'))
    else:
        return render_template("welcome.html")
        #there will be other buttons here

        

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
        
