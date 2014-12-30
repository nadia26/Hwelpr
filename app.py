from flask import Flask, flash, render_template, request, redirect, url_for, session, escape

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
            #this is where all the authentication mongo stuff would go 
            return redirect(url_for('welcome'))
        if request.form['b']=="Sign Up":
            username = request.form["signusername"]
            password = request.form["signpassword"]
            password2 = request.form["signpassword2"]
            name = request.form["name"]
            #this is where all the adding user mongo stuff would go 
            message = "Registration Sucessful! Log In to get started." 
            return render_template("home.html", message=message)
        if request.form['b']=="Cancel":
            return render_template("home.html", message=message)
    
@app.route("/welcome", methods=["GET","POST"])
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
    else:
        return render_template("welcome.html")
        #there will be other buttons here

if __name__=="__main__":
    app.debug=True
    app.run()

        
