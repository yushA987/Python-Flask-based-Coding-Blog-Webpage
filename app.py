from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from  werkzeug.utils import secure_filename
# from flask_mail import Mail, Message
import json
import os
import math

with open('templates/config.json') as c:
    params =json.load(c)["params"]

local_server = params['local_server']

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = params["upload_location"]
# app.config.update(
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_PORT = 465,
#     MAIL_USE_SSL = True,      # do you want to use encryption
#     MAIL_USE_TLS = False,
#     MAIL_USER_NAME = params["user_gmail"],
#     MAIL_PASSWORD = params["user_pass"]
# )

# mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    '''sno, name, phone, email, mes, date'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)

class Posts(db.Model):
    '''sno, slug, title, tagline, content, post_by, time, imgfile'''
    sno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    post_by = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(120), nullable=True)
    imgfile = db.Column(db.String(50), nullable=False)


# Home Route
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params["no_of_posts"]))

    page = request.args.get('page') 
    if (not str(page).isnumeric()):
        page = 1

    page = int(page)
    posts = posts[(page-1)*int(params["no_of_posts"]) : (page-1)*int(params["no_of_posts"]) + int(params["no_of_posts"])]
    if page == 1 and page == last:
        prev = "#"
        next = "#"
    elif page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
        
    return render_template("index.html", params = params, posts = posts, next = next, prev = prev)

# About route
@app.route("/about")
def about():
    return render_template('about.html', params = params)

# Dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():

    if ("user" in session and session["user"] == params["admin_uname"]):
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html', params = params, posts = posts)

    if(request.method == "POST"):
        user_name = request.form.get("uname")
        user_pass = request.form.get("upass")

        if(user_name == params["admin_uname"] and user_pass == params["admin_pass"]):
        # set the session variable to login
            session["user"] = user_name      # "user" ko apne hisab se le skte h kuch bhi.
            posts = Posts.query.filter_by().all()
            flash("Logged in Successfully", "success")
            return render_template('dashboard.html', params = params, posts = posts)
    
    return render_template('login.html', params = params)


#Contact route
@app.route("/contact", methods = ["GET", "POST"])
def contact():
    if (request.method == "POST"):
        '''
        Add entry to the database
        '''
        '''sno, name, phone, email, mes, date'''
        name = request.form.get('name')
        phone = request.form.get('phone_no')
        # print(phone)
        email = request.form.get('email')
        mes = request.form.get('message')
        entry = Contacts(name = name, phone = phone, email = email, mes = mes, date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash('Your form was successfully submitted! We will get back to you soon.', 'success')
        # msg = Message("New Message from Blog" + name,
        #     sender=email,
        #     recipients = params["user_gmail"],
        #     body= mes + '\n' + phone)
        # mail.send(msg)

    return render_template('contact.html', params = params)


# Invidual post route
@app.route("/post/<string:post_slug>", methods = ["GET"])   
# There is a rule to pass `<string:post_slug>` in the function
def post(post_slug):
    posts = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, posts =  posts)


@app.route('/edit/0', methods=['GET', 'POST'])
def edit():
    if ('user' in session and session['user'] == params["admin_uname"]):
        if request.method == "POST":
            post_title = request.form.get("title")
            post_tagline = request.form.get("tagline")
            post_slug = request.form.get("slug")
            post_content = request.form.get("content")
            post_postby = request.form.get("postby")
            post_imgfile = request.form.get("imgfile")
            '''sno, slug, title, tagline, content, post_by, time, imgfile'''
            new_entry = Posts(title = post_title, tagline = post_tagline, slug = post_slug, post_by = post_postby,
                              content = post_content, imgfile = post_imgfile, time = datetime.now())
            db.session.add(new_entry)
            db.session.commit()
            flash("Post added Successfully", "success")
            return redirect("/dashboard")
        
        return render_template("edit.html", params = params)
        # return render_template("dashboard.html", params = params)
    else:
        return render_template("login.html", params = params)
    

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def add(sno):
    if ('user' in session and session['user'] == params["admin_uname"]):
        if request.method == "POST":
            post = Posts.query.filter_by(sno = sno).first()
            '''sno, slug, title, tagline, content, post_by, time, imgfile'''
            post.title = request.form.get("title")
            post.tagline = request.form.get("tagline")
            post.slug = request.form.get("slug")
            post.content = request.form.get("content")
            post.post_by = request.form.get("postby")
            post.imgfile = request.form.get("imgfile")
            db.session.commit() 
            flash("Post edited Successfully", "success")
            return redirect("/dashboard")
            # return sno
        post = Posts.query.filter_by(sno = sno).first()
        return render_template("add_post.html", params = params, post = post)
    else:
        return render_template("login.html", params = params)
    


@app.route('/uploader', methods=['POST'])
def uploader():
    if ('user' in session and session['user'] == params["admin_uname"]):
        if request.method == "POST":
            
            if 'file' not in request.files:
                # return 'No file part'
                flash('No file part, Try again..!!', "danger")
                return redirect("/dashboard")
    
            file = request.files['file']
    
            if file.filename == '':
                flash("No selected File, Try again..!!", "danger")
                return redirect("/dashboard")
                # return 'No selected file'
            
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
                flash("File Uploaded Successfully", "success")
                return redirect("/dashboard")
            else:
                flash("Error, Try again..!!", "danger")
                return redirect("/dashboard")
    else:
        # flash("Logged out Successfully", "success")
        return render_template("login.html", params = params)
    

@app.route("/logout")
def logout():
    session.pop('user')
    # flash("Logged out Successfully", "success")
    return redirect("/dashboard")


@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    if('user' in session and session['user'] == params["admin_uname"]):
        post = Posts.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted Successfully", "success")

    return redirect("/dashboard")