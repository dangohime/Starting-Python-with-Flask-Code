from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, abort, \
    send_from_directory
import sqlite3
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

#Imports for file upload
import imghdr
import os
from werkzeug.utils import secure_filename 

UPLOAD_FOLDER = 'chicken'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}

app = Flask(__name__)

app.secret_key ="ENGR3200"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=2)

#Upload specs
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.config['UPLOAD_PATH'] = 'uploads'

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email 

# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]



# This is to take info from the html templates and display them on the webpage
@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")
#Template stuff ends here

#Database stuff

@app.route('/database', methods=['GET'])
def api_all():
    return jsonify(books)

#end of database stuff

#File Upload Stuff-------------------------------------------------
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def index():
    return render_template('upload.html')

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return "File saved successfully"
 
app.run(host='localhost', port=5000)

#End of file upload stuff------------------------------------------

#Info Page stuff
@app.route("/info")
def info():
    return render_template("info.html")
#End of info page stuff


@app.route("/view")
def view():
    return render_template("view.html",values=users.query.all())


#Now this is for login information.
@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        app.permanent = True
        user = request.form["nm"]
        session ["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email

        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()

        flash("Login Successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
         flash("You are already logged in.")
         return redirect(url_for("user"))
        
        return render_template("login.html")
#Login stuff ends here


#Redirects user
@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email= request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved")
        else:
            if "email" in session:
                email= session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in. Please login to proceed.")
        return redirect(url_for("login"))
#User stuff ends here

#Logout time now
@app.route("/logout")
def logout():
        if "user" in session:
            user= session["user"]
            flash(f"You have been logged out, take care {user}", "info")
            session.pop("user", None)
            # session.pop("email", None)
        return redirect(url_for("login"))
#Logout stuff ends here



if __name__=="__main__":
    db.create_all()
    app.run()