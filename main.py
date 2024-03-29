from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = '4567sdfvbnmkjhgfds456789'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner

    def __repr__(self):
        return "Blog {self.title} by: {self.owner}"

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(1000))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password







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
    titleerror=''
    bodyerror=''
    if request.method =='POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title == '' and blog_body == '':
            titleerror = "You cannot leave this blank!"
            bodyerror="You cannot leave this blank!" 
            return render_template('newpost.html', bodyerror=bodyerror, titleerror=titleerror)
        if blog_title == '':
            titleerror = "You cannot leave this blank!"
            return render_template('newpost.html', titleerror=titleerror)
        if blog_body == '':
            bodyerror="You cannot leave this blank!" 
            return render_template('newpost.html', bodyerror=bodyerror)
        user_id = User.query.filter_by(username=session['username']).first().id
        new_post = Blog(blog_title, blog_body, user_id)
        db.session.add(new_post)
        db.session.commit()
        return render_template('/viewblog.html', blog=new_post)
        
    
    return render_template('/newpost.html')




@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        verifyerror = ''
        passworderror = ''
        usernameerror= ''
        existserror = ''
        existing_user = User.query.filter_by(username=username).first()
        if verify != password or verify == '':
            verifyerror = "Please enter a valid verify password"

        if not 3 < len(password) or " " in password or password == '':
            passworderror = "Please enter a valid password"
        
        if not 3 < len(username) or " " in username or username == '':
            username = ''
            usernameerror = "Please enter a valid username"
# checking if an existing user is true
        if existing_user:
            username = ''
            existserror = "Username already exists"

        if not usernameerror and not verifyerror and not passworderror and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template("signup.html", username = username, usernameerror = usernameerror, verifyerror = verifyerror, passworderror = passworderror, existserror = existserror )
    return render_template('/signup.html')
        
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        usererror = ''
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            usererror = 'Username not found or incorrect password. Please check your spelling or create an account.'
            return render_template('login.html', usererror=usererror)

    return render_template('login.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    del session['username']
    return render_template('login.html')


@app.route('/', methods=['GET'])
def index():
    user = User.query.all()
    return render_template('index.html', user=user)



@app.route('/user', methods=['POST', 'GET'])
def user_page():
    username = request.args.get('q')
    if not username:
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    posts = user.blogs

    return render_template('singleuser.html', user=user, posts=posts)






if __name__ == '__main__':
    app.run()