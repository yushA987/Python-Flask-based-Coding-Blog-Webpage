from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from  werkzeug.utils import secure_filename
# from flask_mail import Mail, Message
import json
import os
import math

with open('templates/config.json') as c:
    params = json.load(c)["params"]

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

class Posts_updated(db.Model):
    '''sno, slug, title, tagline, post_by, time, imgfile, para1, para2, para3, para4'''
    sno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(12), nullable=False)
    # content = db.Column(db.String(200), nullable=False)
    post_by = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(120), nullable=True)
    imgfile = db.Column(db.String(50), nullable=False)
    para1 = db.Column(db.String(200), nullable=False)
    para2 = db.Column(db.String(200), nullable=False)
    para3 = db.Column(db.String(200), nullable=False)
    para4 = db.Column(db.String(200), nullable=False)
    user_ref = db.Column(db.String(50), nullable=False)

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    user_gmail = db.Column(db.String(20), nullable = False)
    user_pass = db.Column(db.String(50), nullable = False)

# Home Route
@app.route("/")
def home():
    posts = Posts_updated.query.filter_by().all()
    last = math.ceil(len(posts) / int(params["no_of_posts"]))

    page = request.args.get('page', default = 1, type = int) 
    print(page)
    # print(str(page).isnumeric())
    # if (not str(page).isnumeric()):
    #     page = 1

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
        posts = Posts_updated.query.filter_by().all()
        return render_template('dashboard.html', params = params, posts = posts)

    if(request.method == "POST"):
        user_name = request.form.get("uname")
        user_pass = request.form.get("upass")

        if(user_name == params["admin_uname"] and user_pass == params["admin_pass"]):
        # set the session variable to login
            session["user"] = user_name      # "user" ko apne hisab se le skte h kuch bhi.
            posts = Posts_updated.query.filter_by().all()
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
    posts = Posts_updated.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, posts =  posts)


# curr_session = []
@app.route('/edit/0', methods=['GET', 'POST'])
def edit():
    # print('user' in session)
    users = Users.query.filter_by().all()
    if ('user' in session and (session['user'] == params["admin_uname"] or any(session["user"] == user.user_gmail for user in users))):
        # temp = Users.query.filter_by(user_gmail = session['user']).user_pass

        if request.method == "POST":

            post_title = request.form.get("title")
            post_tagline = request.form.get("tagline")
            post_slug = request.form.get("slug")
            post_para1 = request.form.get("para1")
            post_para2 = request.form.get("para2")
            post_para3 = request.form.get("para3")
            post_para4 = request.form.get("para4")
            post_postby = request.form.get("postby")
            post_imgfile = request.form.get("imgfile")
            users_x = Users.query.filter_by(user_gmail=session["user"]).first()

            if users_x:
                post_user_ref = users_x.sno
                # Now you can use post_user_ref as needed
            else:
                # Handle case where no user with session["user"] is found
                post_user_ref = None  # or whatever appropriate handling you need

            # print(post_user_ref)
            if len(post_slug) == 0:
                flash("Slug cannot be empty", "danger")
                return redirect("/edit/0")
            
            '''sno, slug, title, tagline, post_by, time, imgfile, para1, para2, para3, para4'''
            new_entry = Posts_updated(title = post_title, tagline = post_tagline, slug = post_slug, post_by = post_postby,
                              para1 = post_para1, para2 = post_para2, para3 = post_para3, para4 = post_para4, 
                              imgfile = post_imgfile, time = datetime.now(), user_ref = post_user_ref)
            db.session.add(new_entry)
            db.session.commit()
            flash("Post added Successfully", "success")
            return redirect("/user_dashboard")
        
        return render_template("add_post.html", params = params)
        # return render_template("dashboard.html", params = params)
    else:
        return render_template("login.html", params = params)
    

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def add(sno):
    users = Users.query.filter_by().all()
    if (('user' in session and (session['user'] == params["admin_uname"] or any(session["user"] == user.user_gmail for user in users))) ):
        if request.method == "POST":
            post = Posts_updated.query.filter_by(sno = sno).first()
            '''sno, slug, title, tagline, content, post_by, time, imgfile'''
            post.title = request.form.get("title")
            post.tagline = request.form.get("tagline")
            temp = request.form.get("slug")
            if len(temp) == 0:
                flash("slug cannot be empty", "danger")
                return redirect("/edit/"+sno)
            
            post.slug = temp
            # post.content = request.form.get("content")
            post.para1 = request.form.get("para1")
            post.para2 = request.form.get("para2")
            post.para3 = request.form.get("para3")
            post.para4 = request.form.get("para4")

            post.post_by = request.form.get("postby")
            post.imgfile = request.form.get("imgfile")
            db.session.commit() 
            flash("Post edited Successfully", "success")
            if session['user'] == params["admin_uname"]:
                return redirect("/dashboard")
            else:
                return redirect("/user_dashboard")
            # return sno
        post = Posts_updated.query.filter_by(sno = sno).first()
        return render_template("edit.html", params = params, post = post)
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
    

# @app.route("/logout")  # @app.route is used as a decorater -> basically functions within a function, helps in code reusability and also, helps in focus on imp part
# def logout():
#     session.pop('user')
#     # flash("Logged out Successfully", "success")
#     return redirect("/dashboard")
# the given function below is the same as above without using decoraters

def logout():
    session.pop('user')
    flash("Logged out Successfully", "success")
    return redirect("/")

app.add_url_rule("/logout", "logout", logout)
# app.add_url_rule("/url", endpoint = '{usually function name}', view function = name of function, methods)

@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    users = Users.query.filter_by().all()
    if('user' in session and (session['user'] == params["admin_uname"] or any(session["user"] == user.user_gmail for user in users))):
        post = Posts_updated.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted Successfully", "success")
    if session["user"] == params["admin_uname"]:
        return redirect("/dashboard")
    return redirect("/user_dashboard")



@app.route('/confirmation/<string:sno>', methods = ['GET', 'POST'])
def modal(sno):
    # pass  
    if('user' in session and session['user'] == params["admin_uname"]):  
        posts = Posts_updated.query.filter_by(sno = sno).first()
        #  return redirect('/dashboard')
        return render_template("modal.html", posts = posts, params = params)
         

@app.route("/user_dashboard", methods = ['POST', 'GET'])
def signIn():
    users = Users.query.filter_by().all()
    posts = Posts_updated.query.filter_by().all()
    if("user" in session and any(session["user"] == user.user_gmail for user in users)):
        matched_user = next(user for user in users if user.user_gmail == session["user"])
        # if matched_user.user_pass
        # print(matched_user.user_gmail)
        if matched_user.user_gmail == params["admin_uname"]:
            return render_template('dashboard.html', params = params, posts = posts, admin = True)
        else:
            posts_user = Posts_updated.query.filter_by(user_ref = matched_user.sno).all()
            return render_template("user_dashboard.html", params = params, posts = posts_user, admin = False)
    
    # elif("user" in session and session["user"] == params["admin_uname"]):
    #     # posts = Posts_updated.query.filter_by().all()
    #     return render_template('dashboard.html', params = params, posts = posts)
    
    if(request.method == "POST"):
        user_name = request.form.get("uname")
        user_pass = request.form.get("upass")


        session["user"] = user_name      # "user" ko apne hisab se le skte h kuch bhi.
        # curr_session.append("user_name")
        if any(session["user"] == user.user_gmail for user in users):
            matched_user = next(user for user in users if user.user_gmail == session["user"])
            # print(f"{matched_user.user_gmail} {matched_user.user_pass}")
            if matched_user.user_pass == user_pass:

                flash("Logged in Successfully", "success")
                return redirect("/user_dashboard")
            else:
                flash("Wrong password.. Try again", "danger")
                session.pop('user')
                return redirect("/")


        new_entry = Users(user_gmail = user_name, user_pass = user_pass)
        db.session.add(new_entry)
        db.session.commit()
        session["user"] = user_name 
        flash("Signed in Successfully", "success")
        return redirect("/")
    
    return render_template("signIn.html", params = params)

# own decorator
# def deco(func):
#     print("hi before func")
#     func()
#     print("hi after func")

# @deco
# def say():
#     print("hello")


# @app.route("/dashboard", methods = ["GET", "POST"])
# def dashboard():

#     if ("user" in session and session["user"] == params["admin_uname"]):
#         posts = Posts_updated.query.filter_by().all()
#         return render_template('dashboard.html', params = params, posts = posts)

#     if(request.method == "POST"):
#         user_name = request.form.get("uname")
#         user_pass = request.form.get("upass")

#         if(user_name == params["admin_uname"] and user_pass == params["admin_pass"]):
#         # set the session variable to login
#             session["user"] = user_name      # "user" ko apne hisab se le skte h kuch bhi.
#             posts = Posts_updated.query.filter_by().all()
#             flash("Logged in Successfully", "success")
#             return render_template('dashboard.html', params = params, posts = posts)
    
#     return render_template('login.html', params = params)

if __name__ == '__main__':
    app.run(debug = True)

