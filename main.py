from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(150))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect("/blog")

@app.route("/blog")
def blog_entries():
    blog_id = request.args.get('id')
    
    if blog_id == None:
        all_entries = Blog.query.all()
        return render_template("blog.html",all_entries=all_entries)
    else:
        entry = Blog.query.get(blog_id)
        return render_template("eachblog.html",entry=entry)
    


@app.route("/newpost",methods=['GET','POST'])
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        title_error = ""
        body_error = ""
    
        if title.strip()=="":
            title_error = "Please fill in the title"
        if body.strip() == "":
            body_error = "Please fill in the body"
        if (not title_error) and (not body_error):
            new_entry = Blog(title, body)
            db.session.add(new_entry)
            db.session.commit()
            return redirect("/blog?id={0}".format(new_entry.id))
        else:
            return render_template("newpost.html",title=title,body=body,title_error=title_error,body_error=body_error)
    else:
        return render_template("newpost.html",title="",body="",title_error="",body_error="")

if __name__ == '__main__':
    app.run()