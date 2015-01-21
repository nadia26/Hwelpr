import datetime
from flask import Flask, flash, render_template, request, redirect, url_for, session, escape
from pymongo import MongoClient
from functools import wraps


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

@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/logout")
def logout():
    session.pop("myuser", None)
    print(session)
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
    return render_template("welcome.html", name=getname(session['myuser']))

@app.route("/profile", methods=["GET","POST"])
@authenticate("/profile")
def profile():
    return render_template("profile.html", name = getname(session['myuser']),
                                                          username = session['myuser'])

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
            tags = request.form['tags']
            addhomework(subject,title,description,summary,content,tags)
            return render_template("addhw.html", message="Homework successfully posted.")
        else:
            return render_template("welcome.html")

@app.route("/myhw", methods=["GET","POST"])
@authenticate("/myhw")
def myhw():
    if request.method=="GET":
        myhomeworks = homeworks.find({"poster":session['myuser']})
        return render_template("myhw.html", homeworks=myhomeworks)
    else:
        return render_template("welcome.html")

@app.route("/myrecs", methods=["GET","POST"])
@authenticate("/myrecs")
def myrecs():
    if request.method=="GET":
        return render_template("myrecs.html")
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
            #if request.form['english']=="english":
            #    print "hi"
            num_results = searchtags(query)[0]
            results = searchtags(query)[1]
            return render_template("search.html",message=str(num_results)+" result(s) found",results=results)
        else:
            return render_template("welcome.html")


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
        print name
        if name['user'] == uname:
            if name['pass'] == pword:
                return True
    return False

def adduser(uname,pword,name):
    if db.info.find_one({'user':uname}) == None:
        d = {'user':uname,'pass':pword, 'name':name}
        db.info.insert(d)
        return True
    return False

#adds homework to database
def addhomework(subject,title,desc,summary,work,tags):
    homework = {"subject":subject,
                "title":title,
                "description":desc,
                "summary":summary,
                "work":work,
                "date":datetime.datetime.utcnow(),
                "poster":session['myuser'],
                "tags_string":tags.lower(),
                "tags_array":tags.lower().split(" ")
                
}
    post_id = homeworks.insert(homework)
    #for testing purposes, prints homeworks in terminal:
    #for homework in homeworks.find():
    #   print(homework)

def searchtags(query):
    #loops through each homework in database looking for tag in common with query
    num_results = 0
    results = []
    for homework in homeworks.find({"tags_array": query}):
        num_results+=1
        results.append(homework)
    return (num_results, results)

if __name__=="__main__":
    client = MongoClient()
    db = client['1258']
    homeworks = db['homeworks']
    app.debug=True
    app.run()
        
