from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    usermame = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(1000))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password






@app.route('/')
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        blogs = Blog.query.all()

    return render_template('/blog.html', blogs=blogs)

@app.route('/viewblog')
def viewblog():
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)
    return render_template('/viewblog.html',blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method =='POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()
        return render_template('/viewblog.html', blog=new_post)
        
    
    return render_template('/newpost.html')




@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
# if statements to check authenticity

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')



@app.route('/index', methods=['POST', 'GET'])
def index():
    pass








if __name__ == '__main__':
    app.run()
