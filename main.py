from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/static'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


#Line below only required once, when creating DB. 


@app.route('/')
def home():

    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form.get('email')
        user_email = User.query.filter_by(email=email).first()
        if user_email:
            error = 'That email already exit. please register another email.'
        else:

            new_user = User(
                name=request.form.get('name'),
                email=request.form.get('email'),
                password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            name = User.query.get(new_user.id).name
            return redirect(url_for('home'))


    return render_template("register.html", error=error)



@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    authenticated = True
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user_email = User.query.filter_by(email=email).first()
        if user_email:
            if check_password_hash(user_email.password, password):
                login_user(user_email)
                authenticated = False
                return redirect(url_for('secrets', authenticated=authenticated))
            else:
                error = 'Password incorrect please try again'
        else:
            error = 'That email does not exist, please try again'

    return render_template("login.html", error=error, authenticated=authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    authenticated = True

    return redirect(url_for('home', authenticated=authenticated))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', filename="file/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
