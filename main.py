from flask import Flask, render_template, request, session, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

with open("config.json", "r") as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)
app.secret_key = "super-secret-key"


if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]


else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["proud_uri"]

db = SQLAlchemy(app)


class Medicines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    medicines = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mid = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    utype = db.Column(db.String(30), nullable=False)
    disease = db.Column(db.String(120), nullable=False)


class Posts(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    medical_name = db.Column(db.String(80), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(120), nullable=False)


class Addmp(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String, nullable=False)
    amount = db.Column(db.String, nullable=False)


class Logs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String, nullable=True)
    action = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(100), nullable=False)


class Users(db.Model):
    usn = db.Column(db.String(10), primary_key=True)  # USN as the primary key
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    utype = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    guardians_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            # Capture the USN and other form data
            usn = request.form.get("usn")
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")
            utype = request.form.get("utype")
            date_of_birth_str = request.form.get("date_of_birth")
            guardians_name = request.form.get("guardians_name")
            phone_number = request.form.get("phone_number")

            # Validate inputs
            if not usn or not username or not password or not email:
                flash("All required fields must be filled!", "danger")
                return render_template("signup.html", params=params)

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Handle date of birth conversion
            date_of_birth = None
            if date_of_birth_str:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

            # Create a new user entry
            entry = Users(
                usn=usn,
                username=username,
                password=hashed_password,
                email=email,
                utype=utype,
                date_of_birth=date_of_birth,
                guardians_name=guardians_name,
                phone_number=phone_number
            )

            print(entry)

            # Add and commit to the database
            db.session.add(entry)
            db.session.commit()
            flash("Data added successfully", "primary")
            return redirect("/login")

        except ValueError as ve:
            flash(f"Invalid input: {ve}", "danger")
            return render_template("signup.html" , params=params)

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            return render_template("signup.html", params=params)

    return render_template("signup.html", params=params)



@app.route("/logout")
def logout():
    session.pop("user")
    session.pop("utype")
    session.pop("usn")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        posts = Posts.query.all()
        return render_template("index.html", params=params, posts=posts)

    if request.method == "POST":
        usn = request.form.get("usn")  # Use USN for login
        password = request.form.get("password")
        user = Users.query.filter_by(usn=usn).first()  # Query by USN for students
        print(user)
        print(user.password)
        print(password)
        print(check_password_hash(user.password, password))
        if user is not None and check_password_hash(user.password, password):
            session["user"] = user.username
            session["usn"] = user.usn
            session["utype"] = user.utype
            posts = Posts.query.all()
            return render_template("index.html", params=params, posts=posts)
        else:
            flash("Invalid USN or Password", "danger")

    return render_template("login.html", params=params)



@app.route("/")
def hello():

    return render_template("index.html", params=params)


@app.route("/index")
def home():

    return render_template("dashbord.html", params=params)


@app.route("/search", methods=["GET", "POST"])
def search():

    if request.method == "POST":

        name = request.form.get("search")
        post = Addmp.query.filter_by(medicine=name).first()

        if post:
            flash("Item Is Available.", "primary")

    return render_template("search.html", params=params)


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html", params=params)


@app.route("/insert", methods=["GET", "POST"])
def insert():

    if request.method == "POST":
        """ADD ENTRY TO THE DATABASE"""
        mid = request.form.get("mid")

        medical_name = request.form.get("medical_name")
        owner_name = request.form.get("owner_name")
        phone_no = request.form.get("phone_no")
        address = request.form.get("address")
        push = Posts(
            mid=mid,
            medical_name=medical_name,
            owner_name=owner_name,
            phone_no=phone_no,
            address=address,
        )
        db.session.add(push)
        db.session.commit()

        flash("Thanks for submitting your details", "danger")

    return render_template("insert.html", params=params)


@app.route("/addmp", methods=["GET", "POST"])
def addmp():

    if request.method == "POST":
        """ADD ENTRY TO THE DATABASE"""

        newmedicine = request.form.get("medicine")
        newamount = request.form.get("amount")

        push = Addmp(
            medicine=newmedicine,
            amount=newamount,
        )
        db.session.add(push)
        db.session.commit()
        flash("Thanks for adding new items", "primary")
    return render_template("search.html", params=params)


@app.route("/list", methods=["GET", "POST"])
def post():

    if "user" in session:
        if session["utype"] == "Student":
            posts = Medicines.query.filter_by(username=session["user"]).all()
            return render_template("post.html", params=params, posts=posts)
        elif session["utype"] == "employee":
            # fetch where username is equal to session['user'] or type is equal to patient
            posts = Medicines.query.filter_by(username=session["user"]).all()
            posts_students = Medicines.query.filter_by(utype="Student").all()
            return render_template(
                "post.html", params=params, posts=posts + posts_students
            )
        else:
            posts = Medicines.query.all()
            return render_template("post.html", params=params, posts=posts)


@app.route("/items", methods=["GET", "POST"])
def items():

    if "user" in session:

        posts = Addmp.query.all()

        # Create a dictionary to hold the latest entry for each medicine
        unique_posts = {}
        for post in posts:
            if post.medicine not in unique_posts or post.sno > unique_posts[post.medicine].sno:
                unique_posts[post.medicine] = post

        # Convert the dictionary back to a list
        latest_posts = list(unique_posts.values())

        return render_template("items.html", params=params, posts=latest_posts)


@app.route("/sp", methods=["GET", "POST"])
def sp():

    if "user" in session:

        posts = Medicines.query.all()
        return render_template("store.html", params=params, posts=posts)


@app.route("/edit/<string:mid>", methods=["GET", "POST"])
def edit(mid):
    if "user" in session and session["user"] == params["user"]:
        if request.method == "POST":
            medical_name = request.form.get("medical_name")
            owner_name = request.form.get("owner_name")
            phone_no = request.form.get("phone_no")
            address = request.form.get("address")

            if mid == 0:
                posts = Posts(
                    medical_name=medical_name,
                    owner_name=owner_name,
                    phone_no=phone_no,
                    address=address,
                )

                db.session.add(posts)
                db.session.commit()
            else:
                post = Posts.query.filter_by(mid=mid).first()
                post.medical_name = medical_name
                post.owner_name = owner_name
                post.phone_no = phone_no
                post.address = address
                db.session.commit()
                flash("data updated ", "success")

                return redirect("/edit/" + mid)
        post = Posts.query.filter_by(mid=mid).first()
        return render_template("edit.html", params=params, post=post)


#         if user is logged in
# delete


@app.route("/delete/<string:mid>", methods=["GET", "POST"])
def delete(mid):
    if "user" in session:
        post = Posts.query.filter_by(mid=mid).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "warning")

    return redirect("/login")


@app.route("/deletemp/<string:id>", methods=["GET", "POST"])
def deletemp(id):
    if "user" in session:
        post = Medicines.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "primary")

    return redirect("/list")


@app.route("/medicines", methods=["GET", "POST"])
def medicine():
    if request.method == "POST":
        """ADD ENTRY TO THE DATABASE"""
        mid = "100"
        name = request.form.get("name")
        medicines = request.form.get("medicines")
        email = request.form.get("email")
        amount = request.form.get("amount")
        disease = request.form.get("disease")
        username = session["user"]
        utype = session["utype"]
        entry = Medicines(
            mid=mid,
            name=name,
            medicines=medicines,
            email=email,
            amount=amount,
            username=username,
            utype=utype,
            disease=disease,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Data Added Successfully", "primary")

    return render_template("medicine.html", params=params)



@app.route("/profile")
def profile():
    if "user" in session and session["utype"] == "Student":
        # Fetch the student's details based on their USN
        user = Users.query.filter_by(usn=session["usn"]).first()
        
        if user:
            return render_template("student_profile.html", user=user, params=params)
        else:
            flash("User not found", "danger")
            return redirect("/login")
    else:
        flash("Access Denied", "danger")
        return redirect("/login")




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
