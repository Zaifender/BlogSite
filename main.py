from flask import Flask,render_template,redirect,url_for,session,request,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "jojo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3' #COPY PASTA 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    author = db.Column(db.String(100),primary_key=True)
    password = db.Column(db.String(100))

    def __init__(self,author,password):
        self.author = author
        self.password = password

class posts(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    author = db.Column(db.String(100), db.ForeignKey('users.author'))
    title = db.Column(db.String(100))
    content = db.Column(db.String(5000))

    def __init__(self,author,title,content):
        self.author = author
        self.title = title
        self.content = content
        

@app.route("/",methods=["GET","POST"])
def home():

    P=[]
    allpost = posts.query.all()
    for i in allpost:
        p = {"author":i.author,"title" : i.title, "content": i.content,"id":i._id}
        P.append(p)

    if request.method=="POST":
        title = request.form["c"]
        session["title"] = title
        return redirect(url_for("post"))
        
    if request.method=="GET":
        if "user" in session:
            return render_template("home.html",login=True,cards=P)
        else:
            return render_template("home.html",login=False,cards=P)
    
@app.route("/login",methods=["POST","GET"])
def login():

    if request.method=="POST":
        user = request.form["u"]
        password = request.form["p"]

        user_found = users.query.filter_by(author=user).first()
        if user_found:
            if password == user_found.password:
                session["user"] = user
                session["password"] = password
    
                flash("Logged in Successfully")
                return redirect(url_for("home"))
            else:
                flash("Incorrect password")   
        else:
            flash("You have to Sign up first!")  

    return render_template("login.html")


@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":

        user = request.form["u"]
        password = request.form["p"]
        cpassword = request.form["cp"]

        user_found = users.query.filter_by(author=user).first()
        if user_found:
            if password == user_found.password:
                session["user"] = user
                session["password"] = password
                flash("User was Already Registered")
                flash("Logged in successfully")
                return redirect(url_for("home"))
    
        else:
            if cpassword==password:
                session["user"] = user
                session["password"] = password
                usr = users(user,password=password)
                db.session.add(usr)
                db.session.commit()

                flash("Signed up successfully")
                return redirect(url_for("home"))
            else:
                flash("Fill the Password Correctly!")

            
    return render_template("signup.html")

@app.route("/view",methods=["POST","GET"])
def view():
    if request.method == "POST":
        us = request.form["id"]

        if "user" in session and us == session["user"]:
            session.pop("user",None)
            session.pop("password",None)
        
        users.query.filter_by(author=us).delete()
        db.session.commit()

    return render_template("view.html", values=users.query.all())

@app.route("/create",methods=["POST","GET"])
def create():
    if "user" in session:
        if request.method == "POST":
            title = request.form["t"]
            content = request.form["c"]
            author = session["user"]

            post = posts(author=author,title=title,content=content)
            db.session.add(post)
            db.session.commit()

            flash("Post Uploaded!")
            return redirect(url_for("home"))

        else:
            return render_template("create.html",details=[],login=True)
    else:
        flash("You have to login/SignUp first!")
        return redirect(url_for("home"))

@app.route("/post")
def post():

    title = session["title"] #from home
    user_found = posts.query.filter_by(title=title).first()
    if user_found:
        title = user_found.title
        content = user_found.content
        author = user_found.author
        D = {"title":title,"content":content,"author":author}
        if "user" in session:
            return render_template("post.html",details=D,login=True)
        else:
            return render_template("post.html",details=D,login=False)

@app.route("/edit",methods=["POST","GET"])
def edit():
    if "user" in session:
        
        if request.method=="POST":
            session["id"] = request.form["id"]
            return redirect(url_for("editpost"))
            
        else:
            P=[]
            allpost = posts.query.filter_by(author=session["user"]).all()
            for i in allpost:
                p = {"id":i._id,"author":i.author,"title" : i.title, "content": i.content}
                P.append(p)
            return render_template("edit.html",cards=P,login=True)
    else:
        flash("You have to login/SignUp first!")
        return redirect(url_for("home"))

@app.route("/editpost",methods=["POST","GET"])
def editpost():
    if "user" in session:
        if request.method=="POST":
            id = session["id"]
            title = request.form["t"]
            content = request.form["c"]

            post_found = posts.query.filter_by(_id=id).first()
            if post_found:

                post_found.title = title
                post_found.content = content
                db.session.commit()
            flash("Post Updated!")
            return redirect(url_for("home"))
        
        else:
            id = session["id"]
            user_found = posts.query.filter_by(_id=id).first()
            if user_found:
                title = user_found.title
                content = user_found.content
                author = user_found.author
                D = {"title":title,"content":content,"author":author}
                return render_template("create.html",details=D,login=True)

@app.route("/delete",methods=["POST"])
def delete():
    if request.method=="POST":
        id = request.form["id"]
        user_found = posts.query.filter_by(_id=id).first()
        if user_found:
            posts.query.filter_by(_id=id).delete()
            db.session.commit()
            flash("Post deleted")
            return redirect(url_for("home"))
    else:
        return "Error"


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user",None)
        session.pop("password",None)
        flash("Logged out successfully!")
    else:
        flash("Not logged in yet!")

    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)