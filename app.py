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
    return render_template("todo.html", homeworks = homeworks.find({"assignedTo": session['myuser'], "status": "in progress"}), TDnum = getTDnum(), MYHWnum = getMYHWnum())

@app.route("/profile", methods=["GET","POST"])
@authenticate("/profile")
def profile():
    if request.method=="GET":
        return render_template("profile.html",
                               name = getname(session['myuser']),
                               username = session['myuser'],
                               points = getpoints(session['myuser']),
                               MYHWnum = getMYHWnum(),
                               TDnum = getTDnum())
    else:
        if request.form['b']=="Edit profile":
            return redirect(url_for('editprofile'))

@app.route("/editprofile", methods=["GET","POST"])
@authenticate("/editprofile")
def editprofile():
    if request.method=="GET":
        return render_template("editprofile.html", name = getname(session['myuser']),
                               username = session['myuser'],TDnum = getTDnum(), MYHWnum = getMYHWnum())
    else:
        if request.form['b']=="Update":
            message = ""
            newname = request.form['name']
            newusername = request.form['username']
            bio = request.form['bio']
            user = db.info.find_one({'user':session['myuser']})
            if newname != None:
                #db.info.update({'user':session['myuser']},
                #               {"$set":{'name':newname}},
                #               upsert = True)
                user['name'] = newname
                print "\n\n\n\n"
                print user['name']
                print "\n\n\n\n"
            if newusername != None:
                #db.info.update({'user':session['myuser']},
                #               {"$set":{'user':newusername}},
                #  upsert = True)
                user['user'] = newusername
            if bio != None:
                #db.info.update({'user':session['myuser']},
                #               {"$set":{'bio':bio}},
                 #              upsert = True)
                user['bio'] = bio
            db.info.save(user)
            message = "Update sucessful!" 
            return render_template("editprofile.html", message=message, name=newname, TDnum = getTDnum(), MYHWnum = getMYHWnum())


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
            work = request.form['work']
            tags = request.form['tags']
            due = request.form['due']
            if (title == "" or description == "" or work == "" or due == ""):
                return render_template("addhw.html", message = "Please fill in all fields.", TDnum=getTDnum(), MYHWnum=getTDnum())
            addhomework(subject,title,description,work,due,tags)
            return render_template("addhw.html", message="Homework successfully posted.", TDnum = getTDnum(), MYHWnum = getMYHWnum())

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
    return render_template("myrecs.html",
                           homeworks = homeworks.find(),
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
        user['points'] = user['points'] + 1
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
        return render_template("search.html",
                               message= str(results.count()) + " result(s) found",
                                results=results, subject=subject, subjects=subjects, user = session['myuser'],
                                TDnum = getTDnum(),
                                MYHWnum = getMYHWnum())

"""
def searchtags(query, subject):
    #loops through each homework in database looking for tag in common with query
    num_results = 0
    results = []
    if (subject!="None"):
        for homework in homeworks.find({"subject": subject, "tags_array": query}):
            num_results+=1
            results.append(homework)
    else:
        for homework in homeworks.find({"tags_array": query}):
            num_results+=1
            results.append(homework)
    return (num_results, results)
"""

def getname(uname):
    users = db.info.find()
    for user in users:
        if user['user'] == uname:
            return user['name']

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

def adduser(uname,pword,name):
    if db.info.find_one({'user':uname}) == None:
        bio = ""
        #we still have to add other database elements (like rankings and stuff)
        d = {'user':uname,'pass':pword, 'name':name, 'bio':bio, 'points': 0}
        db.info.insert(d)
        return True
    return False

#adds homework to database (WIP):
def addhomework(subject,title,desc,work,due,tags):
    homework = {"subject":subject,
            "title":title,
            "description":desc,
            "work":work,
            "date": str(datetime.date.today()),
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
    app.run()
