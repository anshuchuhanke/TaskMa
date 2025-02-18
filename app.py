from flask import Flask, render_template, request, redirect, url_for, session ,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/")
def home():
    return render_template('index.html')

@app.route('/register' , methods=["GET" , "POST"])
def register():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already taken!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for("login"))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['login']
        password = request.form['password']

        # Check if user exists (by email or username)
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        # ✅ Step 3: Prevents "NoneType" error if user is not found
        if not user:
            return "Invalid email or password!", 401  # Or render a template with an error message

        # Check if password is correct
        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # Store user in session
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password!", 401  # Wrong password

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in
    user = User.query.get(session['user_id'])  # Get logged-in user details
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))  # Redirect to login page

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=8080)
