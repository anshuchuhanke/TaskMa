from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash



app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///user.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'QWERTY'
db=SQLAlchemy(app)

#user model
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80),nullable=False,unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(80),nullable=False)

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

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for("login"))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the user from the database
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):  # Check if password matches
            return redirect(url_for('dashboard'))  # Redirect to dashboard or user page
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    
    return render_template('login.html')


with app.app_context():
    db.create_all()

if __name__ =="__main__":
    app.run(debug=True , port=8080)
