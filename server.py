from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
import os

# Initialize Flask app
app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stewardwell.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_code = db.Column(db.String(10), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', backref='family', lazy=True, foreign_keys='User.family_id')
    children = db.relationship('Child', backref='family', lazy=True)
    
    @staticmethod
    def generate_family_code():
        """Generate a unique 6-character family code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Family.query.filter_by(family_code=code).first():
                return code

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def landing():
    return render_template('public/landing/index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('public/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('public/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_family = None
    children = []
    if current_user.family_id:
        user_family = Family.query.get(current_user.family_id)
        children = Child.query.filter_by(family_id=current_user.family_id).all()
    
    return render_template('private/dashboard/index.html', family=user_family, children=children)

@app.route('/create_family', methods=['POST'])
@login_required
def create_family():
    if current_user.family_id:
        flash('You are already part of a family')
        return redirect(url_for('dashboard'))
    
    family_name = request.form['family_name']
    family_code = Family.generate_family_code()
    
    family = Family(name=family_name, family_code=family_code, creator_id=current_user.id)
    db.session.add(family)
    db.session.commit()
    
    # Add user to family
    current_user.family_id = family.id
    db.session.commit()
    
    flash(f'Family created! Family code: {family_code}')
    return redirect(url_for('dashboard'))

@app.route('/join_family', methods=['POST'])
@login_required
def join_family():
    if current_user.family_id:
        flash('You are already part of a family')
        return redirect(url_for('dashboard'))
    
    family_code = request.form['family_code'].upper()
    family = Family.query.filter_by(family_code=family_code).first()
    
    if family:
        current_user.family_id = family.id
        db.session.commit()
        flash(f'Successfully joined {family.name}!')
    else:
        flash('Invalid family code')
    
    return redirect(url_for('dashboard'))

@app.route('/add_child', methods=['POST'])
@login_required
def add_child():
    if not current_user.family_id:
        flash('You must be part of a family to add children')
        return redirect(url_for('dashboard'))
    
    name = request.form['child_name']
    age = request.form.get('child_age')
    age = int(age) if age and age.isdigit() else None
    
    child = Child(name=name, age=age, family_id=current_user.family_id, created_by=current_user.id)
    db.session.add(child)
    db.session.commit()
    
    flash(f'Child {name} added to the family!')
    return redirect(url_for('dashboard'))

@app.route('/delete_child/<int:child_id>')
@login_required
def delete_child(child_id):
    child = Child.query.get_or_404(child_id)
    
    # Check if user is in the same family as the child
    if current_user.family_id != child.family_id:
        flash('You can only delete children from your own family')
        return redirect(url_for('dashboard'))
    
    db.session.delete(child)
    db.session.commit()
    flash(f'Child {child.name} removed from the family')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
