import os
import secrets
from PIL import Image
from flask import Flask, redirect, url_for, render_template, request, session, flash, g, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "weAreCoolest"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

db = SQLAlchemy(app)
db1 = SQLAlchemy(app)
# db2 = SQLAlchemy(app)

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key= True)
    username = db.Column("username", db.String(100))
    password = db.Column("password", db.String(100))
    bud = db.Column("bud", db.Boolean)
    activity = db.Column("activity", db.String(100))
    streak = db.Column("streak", db.Integer, primary_key=True)
    bio = db.Column("bio", db.String(300))
    achieve = db.Column("achieve", db.String(300))
    joke = db.Column("joke", db.String(200))
    budName = db.Column("buddy",db.String(200))
    image_file = db.Column("img", db.String(100), default="sunflowers.jpg")
    lastCheckIn= db.Column(db.DateTime, default=None)
    
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.activity = None
        self.streak = 0
        self.bud = True #should automatically signal they want a buddy unless they change it
        self.bio = "I love donuts! Let's be good buddies :D" 
        self.achieve = "I want to be more consistent with self care"
        self.joke = "Why can’t you be friends with a squirrel?... They drive everyone nuts!"
        self.budName = None
        
        
    def __repr__(self):
        return self.username

class newActivity(db1.Model):
     id1 = db1.Column("id1", db1.Integer, primary_key= True)
     activityname= db1.Column("activityname", db1.String(100))
     description = db1.Column(db1.Text, default=("No Description"))

     def __init__(self,activityname):
         self.activityname=activityname
    
     def __repr__(self):
         return self.activityname

# class checkInTimes():
#     id2=db2.Column("id2", db2.Integer, primary_key=True)
#     timeCheckIn= db2.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return self.timeCheckIn

db.create_all()
db.session.commit()


db1.create_all()
db1.session.commit()

# db2.create_all()
# db2.session.commit()

# walk = newActivity("Walk")
# walk.description = "Take a nice walk outside"
# journal = newActivity("Journal")
# journal.description = "Write down how you're feeling!"
# meditation = newActivity("Meditation")
# meditation.description = "Meditate for half an hour :)"

# db1.session.add(walk)
# db1.session.add(journal)
# db1.session.add(meditation)
# db1.session.commit()
# i want to see if these can be the default ones

@app.before_request
def before_request():
    g.user = None
    if User:
        if 'name' in session and not(session['name'] == None):
            user = User.query.filter_by(username = session['name']).first()
            g.user = user
    

@app.route("/")
@app.route('/home')
def home():
    if User == None or len(User.query.all())==0:
        flash("Last user was not properly logged out - logging out!")
        return redirect("logout")
    elif 'name' in session:
        found_user = User.query.filter_by(username = session['name']).first()
        if found_user:
            return render_template("index.html", values=User.query.all(),userFound=True,user=found_user,numUsers=User.query.count())
        else:
            session.pop("name",None)
            return render_template("index.html",userFound=False,numUsers=User.query.all().count())
    else:
        return render_template("index.html", values=User.query.all(),userFound=False,numUsers=User.query.count())

@app.route('/<name>', methods=['POST','GET'])
def viewBuddy(name):
    if not 'name' in session:
        flash("You need to login first!")
        return render_template("index.html",userFound=False,numUsers=User.query.count())
    buddy = User.query.filter_by(username=name).first()
    user = User.query.filter_by(username=session['name']).first()
    if buddy == None:
        flash("No Buddy!")
        return render_template("index.html",userFound=False,numUsers=User.query.count())
    if request.method=='POST' and request.form['button'] == 'Be Buddies':
        flash("Successfully became buddies!")
        buddy.budName = session['name']
        user.budName = buddy.username
        user.bud = False
        buddy.bud = False
        db.session.commit()
    if request.method=='POST' and request.form['button'] == 'Change Buddies':
        flash("You have to remove your current buddy to change buddies!")
        # redirect(url_for("/<user.budName>"))
    # <p>You have to remove {{user.budName}} as a buddy to be {{buddy.username}}'s buddy :(</p>
    return render_template("buddy.html", buddy=buddy, user=user)
    
@app.route("/profile", methods=["POST", "GET"])
def profile():
    
    #the profile image part after adding new column dont delete
    #image_file = url_for('static', filename='images/' + User.image_file)

    if "name" in session:
        user = User.query.filter_by(username=session['name']).first()

        if user == None:
            flash("Cannot find user. Try Again!")
            return redirect(url_for("home"))

        #print("it works at this line")
        # print(request.method)
        if request.method=="POST":
            if request.form['button'] == 'Remove Buddy':
                flash("Buddy removed :(")
                budName = user.budName
                buddy = User.query.filter_by(username=budName).first()
                user.budName = None
                buddy.budName = None
                user.bud = True
                buddy.bud = True
                db.session.commit()
                return render_template('profile.html', user=user)
            elif request.form["button"]== "Check In":
                if 'name' in session:
                    user = User.query.filter_by(username=session['name']).first()
                    if user.streak==0:
                        user.lastCheckIn= datetime.now()
                        user.streak=1
                    else:
                        difference = datetime.now() - user.lastCheckIn
                        daysPassed = difference.days
                        if (daysPassed >= 1):
                            user.streak= user.streak+1
                            user.lastCheckIn=datetime.now()
                            user.streak= user.streak+1
                        else:
                            flash("You already checked in once today!")
                    db.session.commit()
                return render_template('profile.html', user=user)
            else:
                bio = request.form["bio"]
                achieve = request.form["achieve"]
                joke = request.form["joke"]
                pfp = request.files["pfp"]

                if bio:
                    user.bio = bio
                if achieve:
                    user.achieve = achieve
                if joke:
                    user.joke = joke
                if pfp:
                    flash("Profile Successfully Changed")
                    # print("AJDSNAJDFSAJFSAJFNADKJA")
                    #filename = secure_filename(pfp.filename)
                    picture_file = save_picture(pfp)
                    user.image_file = picture_file
                    
                db.session.commit()
                return render_template('profile.html', user=user)
        else:
            return render_template('profile.html', user=user)
    else:
        flash("You must login first!")
        return redirect(url_for("login"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/activity", methods=["POST", "GET"])
def activity():
    if request.method == "POST":
        activity=request.form["activity"]
        description=request.form["description"]
        
        find_act=newActivity.query.filter_by(activityname=activity).first()
        if find_act:
            flash("activity already exists")
            session["activityname"] = find_act.activityname
        else:
            actname = newActivity(activity)
            if description:
                actname.description = description
            flash("new activity added")
            db1.session.add(actname)
            db1.session.commit()
            
    if (newActivity.query.first == None):
        return render_template("activity.html")
    return render_template("activity.html",activities=newActivity.query.all())
    

@app.route("/Meditation",methods=["POST", "GET"])
def meditation():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Meditation"
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Meditation.html")

@app.route("/Journal",methods=["POST", "GET"])
def journal():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Journaling"
            db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Journal.html")

@app.route("/Walk",methods=["POST", "GET"])
def walk():
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = "Walking"
            db.session.commit()
            return redirect(url_for("profile"))
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
        #print(user)
        #print(user)
        #print(user[0])
        if user and user.password == password:
            session['name'] = user.username
            flash("Login Successful!")
            return redirect(url_for('profile'))
        elif user:
            flash("Wrong password")
            return redirect(url_for("login"))
        else:
            flash("No account with that username exists. Please create a new acc!")
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
            session['name'] = newusername
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("questions", user=usr))
    else:
        return render_template("create.html")

@app.route("/Questions", methods=["POST", "GET"])
def questions():
    user = User.query.filter_by(username=session['name']).first()
    if request.method == "POST":
        if "name" in session:
            session.permanent = True

            # user.bio=request.form["bio"]
            # user.achieve=request.form["achieve"]
            # user.joke=request.form["joke"]
            # db.session.commit()
            return redirect(url_for("profile"))
    return render_template("Questions.html", user=user)


@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all(), values1=newActivity.query.all())

@app.route("/")

@app.route("/edit", methods=["POST", "GET"])
def edit():
    if "name" in session:
        user = User.query.filter_by(username=session['name']).first()
        if request.method=="POST":
        # if request.method=="POST" and (request.form["buddy"]== "yes" or request.form["buddy"]== "no"):
            flash("Buddy Status Changed!")
            buddy = request.form["buddy"]
            if buddy == "no":
                user.bud = False
            else:
                user.bud = True
            db.session.commit()
            return redirect(url_for('profile', user=user))
        return render_template('edit.html',user=user)
    return render_template("profile.html")


@app.route('/addActivity')
def addActivity():
    return render_template("addActivity.html")

@app.route("/activity/<activityName>", methods=["POST", "GET"])
def activityPage(activityName):
    
    activity = newActivity.query.filter_by(activityname=activityName).first()
    
    if request.method == "POST":
        if "name" in session:
            flash("yay!")
            user = User.query.filter_by(username=session['name']).first()
            user.activity = activityName
            db.session.commit()
            return redirect(url_for("profile"))
        
    return render_template("chooseActivity.html", act=activity) 



@app.route("/logout")
def logout():
    if 'name' in session:
        flash("You have been logged out!", "info")
        session.pop("name", None)
    else:
        flash("Logging out? You aren't even logged in yet!")
    return redirect(url_for("login"))

 
if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True) 