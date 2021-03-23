import os
import hashlib
from flask import Flask
from flask import Flask, render_template, redirect, url_for, request, session, g, ForeignKey, String
from flask_sqlalchemy import SQLAlchemy
from .authorization import requires_authorization

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "kanbandb.db"))

# Initializes app and databases objects
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.secret_key = "super secret"
signin = LoginManager()
signin.init_app(app)
db = SQLAlchemy(app)


# Initializes Users and Tasks as Python objects
class Task(db.Model):
    '''
    Define task name and status as well as connect it to the user table.
    '''
    __tablename__ = 'Task'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    # deadline = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return "<Title: {}>".format(self.title)


class User(db.Model):
    '''
    Define user names, passwords, and their tasks.
    '''
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    salt = db.Column(String)
    task_id = db.relationship('Task', backref='user', lazy='dynamic')
    def __repr__(self):
        return "<Username: {}>".format(self.username)


# Creates database for users and tasks
db.create_all()
# Generates entries for the database
db.session.commit()


# Starts the web-app with the Sign-In
@app.route('/', methods=['GET', 'POST'])
def welcome():
    '''
    Redirect users to the signin page.
    '''
    return redirect('signin')



# Function and route to register new users
@app.route('/signup', methods=['GET','POST'])
def signup():
    '''
    Sign users up.
    '''
    if request.method == 'POST':
        # Checks password requirements
        if len(request.form['password']) < 10:
            error = 'The password must be at least 10 characters long. Please, try again.'
            return render_template('signup.html', error=error)

        simple_password = request.form['password']
        salt = salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'), 
            salt, 
            100000 
        )

        new_user = User(username=request.form['username'], password=key, salt=salt)

        db.session.add(new_user)
        db.session.commit()
        return redirect("/signin")
    elif request.method == 'GET':
        return render_template('signup.html')



@app.route('/signin', methods=['GET', 'POST'])
@requires_authorization
def signin():
    ''' 
    Sign in existing users.
    '''
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        # Check whether credentials are valid
        if user is None:
            error = 'Invalid credentials. Please, try again.'
            return render_template('signin.html', error=error)
        login_user(user)
        return redirect("/main")
    elif request.method == 'GET':
        return render_template('signin.html')


@app.route('/logout', methods=['GET', 'POST'])
@requires_authorization
def logout():
    '''
    Logs users out of the Index Page to the Sign-In page.
    '''
    session.pop('logged_in', None)
    return redirect('signin')


@app.route('/main', methods=["GET", "POST"])
# Revises whether the user is registered to access its own index page
@requires_authorization
def index():
    '''
    Add tasks to the Kanban Board
    '''
    g.user = current_user
    tasks = None
    error = None
    if request.form:
        try:
            # Ensure tasks are unique
            if request.form.get("title") in [task.title for task in Task.query.all()]:
                error = "Task already exists."
            else:
                task = Task(id = 1, title=request.form.get("title"), status=request.form.get("status"), user_id = g.user.id) 
                tasks = Task.query.all()

                db.session.add(task)
                db.session.commit()
        except Exception as e:
            print("Failed to add task")
            print(e)
    # Sort tasks according to their status
    tasks = Task.query.filter_by(user_id=g.user.id).all()
    todo = Task.query.filter_by(status='todo',user_id=g.user.id).all()
    doing = Task.query.filter_by(status='doing',user_id=g.user.id).all()
    done = Task.query.filter_by(status='done',user_id=g.user.id).all()
    return render_template("index.html", error=error, tasks=tasks, todo=todo, doing=doing, done=done, myuser=current_user)



@app.route("/update", methods=["POST"])
@requires_authorization
def update():
    '''
    Move tasks to other categories.
    '''
    try:
        newstatus = request.form.get("newstatus")
        name = request.form.get("name")
        task = Task.query.filter_by(title=name).first()
        task.status = newstatus
        db.session.commit()
    except Exception as e:
        print("Couldn't update task status")
        print(e)
    return redirect("/main")

@app.route("/delete", methods=["POST"])
@requires_authorization
def delete():
    '''
    Delete tasks.
    '''
    title = request.form.get("title")
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/main")

if __name__ == "__main__":
    app.run(debug=False)