from flask import Flask, request, redirect, render_template, session,flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(150))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='blog.owner_id')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog_entries']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.order_by("username").all()
    return render_template('index.html',users=users)

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            username_error = "Invalid username"
            return render_template('login.html',username_error = username_error, username='')
        elif not password == user.password:
            password_error = "Invalid Password"
            return render_template('login.html',password_error = password_error,username=username)
        else:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html')


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        if username == '' or len(username) < 3:
            username_error = "That's not a valid user name"

        if password == '' or len(password) < 3:
            password_error = "That's not a valid password"

        if verify == '' or password != verify:
            verify_error = "passwords don't match"
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            username_error = "A user with that username already exists"
        
        if username_error or password_error or verify_error:
            return render_template('signup.html',username=username,username_error=username_error,password_error=password_error,verify_error=verify_error)
        
        new_user = User(username,password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username

        return redirect('/newpost')

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/blog")

@app.route("/blog")
def blog_entries():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if user_id:
        all_entries = Blog.query.filter_by(owner_id=user_id).join(User).add_columns(User.username,Blog.title,Blog.body,Blog.id,Blog.owner_id).all()
        return render_template("blog.html",all_entries=all_entries)
    if blog_id:
        entry = Blog.query.filter_by(id=blog_id).join(User).add_columns(User.username,Blog.title,Blog.body,Blog.id,Blog.owner_id).first()
        return render_template("eachblog.html",entry=entry)
    
    all_entries = Blog.query.join(User).add_columns(User.username,Blog.title,Blog.body,Blog.id,Blog.owner_id).all()
    return render_template('blog.html',all_entries=all_entries)
    


@app.route("/newpost",methods=['GET','POST'])
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        
        title_error = ""
        body_error = ""
    
        if title.strip()=="":
            title_error = "Please fill in the title"
        if body.strip() == "":
            body_error = "Please fill in the body"
        if (not title_error) and (not body_error):
            new_entry = Blog(title, body, owner.id)
            db.session.add(new_entry)
            db.session.commit()
            return redirect("/blog?id={0}".format(new_entry.id))
        else:
            return render_template("newpost.html",title=title,body=body,title_error=title_error,body_error=body_error)
    else:
        return render_template("newpost.html",title="",body="",title_error="",body_error="")

if __name__ == '__main__':
    app.run()