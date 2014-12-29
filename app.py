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
    
if __name__=="__main__":
    app.debug=True
    app.run()
        
