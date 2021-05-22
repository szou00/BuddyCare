from flask import Flask, redirect, url_for, render_template, request, session, flash, g
from datetime import timedelta, datetime

from flask.signals import Namespace
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "weAreCoolest"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

db = SQLAlchemy(app)
db1 = SQLAlchemy(app)
class User(db.Model):
    id = db.Column("id", db.Integer, primary_key= True)
    username = db.Column("username", db.String(100))
    password = db.Column("password", db.String(100))
    bud = db.Column("bud", db.Boolean)
    activity = db.Column("activity", db.String(100))
    streak = db.Column("streak", db.Integer, primary_key=True)
    

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.activity = None
        self.streak = 0
        self.bud = True #should automatically signal they want a buddy unless they change it
        # INSERT INTO db (id, username, password) VALUES (0,TRUE)
        
        
    def __repr__(self):
        return self.username

class newActivity(db.Model):
     id1 = db.Column("id1", db.Integer, primary_key= True)
     activityname= db.Column("activityname", db.String(100))

     def __init__(self,activityname):
         self.activityname=activityname
     

db.create_all()
db.session.commit()

@app.before_request
def before_request():
    g.user = None
    if 'name' in session:
        user = User.query.filter_by(username = session['name']).first()
        g.user = user

@app.route("/")
@app.route('/home')
def home():
    if 'name' in session:
        found_user = User.query.filter_by(username = session['name']).first()
        return render_template("index.html", values=User.query.all(),user=found_user)

@app.route('/<name>')
def viewBuddy(name):
    buddy = User.query.filter_by(username=name).first()
    if buddy == None:
        flash("No Buddy!")
        return render_template("index.html")
    return render_template("buddy.html",name=buddy.username,id=buddy.id, activity=buddy.activity,streak=buddy.streak,bud=buddy.bud)
    
@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "name" in session:
        user = User.query.filter_by(username=session['name']).first()

        if user == None:
            flash("Cannot find user")
            return redirect(url_for("home"))

        if request.method=="POST":
            flash("Buddy Status Changed!")
            buddy = request.form["buddy"]
            if buddy == "no":
                user.bud = False
            else:
                user.bud = True
            db.session.commit()
        return render_template('profile.html', content=user.username, id=user.id, activity=user.activity,streak=user.streak,bud=user.bud)
    flash("You must login first!")
    return redirect(url_for("login"))

@app.route("/activity")
def activity():
    if request.method == "POST":
        find_act=newActivity.query.filter_by(activityname=crazy).first()
        if find_act:
            session["activityname"] = find_act.activityname
        else:
            actname = newActivity(activity, "")
            db1.session.add(actname)
            db1.session.commit()
        return redirect(url_for("login"))
    return render_template("activity.html")
    

@app.route("/Meditation")
def meditation():
    return render_template("Meditation.html")

@app.route("/Journal")
def journal():
    return render_template("Journal.html")

@app.route("/Walk")
def walk():
    return render_template("Walk.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]

        #db 
        # user = [x for x in users if x.username == username][0]
        user = User.query.filter_by(username=username).first()
        print(user)
        #print(user)
        #print(user[0])
        if user and user.password == password:
            session['name'] = user.username
            flash("Login Successful!")
            return redirect(url_for('profile'))
        else:
            flash("Login Unsuccessful :(")
            return redirect(url_for("login"))
    else: 
        if "name" in session:        
            flash("Already Logged In!")
            return redirect(url_for("home"))
        return render_template("login.html")

@app.route("/create", methods=["POST","GET"])
def create():
    
    if request.method == "POST":
        newusername = request.form["newusername"]
        newpassword = request.form["newpassword"]
        found_user = User.query.filter_by(username=newusername).first()
        
        if found_user:
            flash("That username is already taken!")
            return render_template("create.html")
        else:
            
            flash("Congrats! You have created a new account.")
            usr = User(len(User.query.all())+1, newusername, newpassword) 
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("questions"))
    else:
        return render_template("create.html")

@app.route("/Questions", methods=["POST", "GET"])
def questions():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("Questions.html")


@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all())

@app.route("/finder")
def finder():
    return render_template("finder.html", values = User.query.all())
    
@app.route("/<user>/edit", methods=["POST", "GET"])
def edit(user):
    # print("hey")
    # if request.method == 'POST':
    #     print("Your buddy status is")
    #     buddyStatus = request.form['buddy']
    #     print(buddyStatus)
    #     found_user = User.query.filter_by(username=user).first()
    #     if found_user:
    #         found_user.bud = buddyStatus
    return render_template("edit.html")

@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("name", None)
    #session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True) 