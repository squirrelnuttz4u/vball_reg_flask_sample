from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volleyball_camp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class CampSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    current_enrollment = db.Column(db.Integer, default=0)
    
    @property
    def available_spots(self):
        return self.max_capacity - self.current_enrollment
    
    @property
    def is_full(self):
        return self.current_enrollment >= self.max_capacity

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)
    camp_session_id = db.Column(db.Integer, db.ForeignKey('camp_session.id'), nullable=False)
    waiver_signed = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    camp_session = db.relationship('CampSession', backref=db.backref('registrations', lazy=True))

# US States for dropdown
US_STATES = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming')
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Validation
        errors = []
        
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        dob_str = request.form.get('dob', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '')
        zipcode = request.form.get('zipcode', '').strip()
        camp_session_id = request.form.get('camp_session_id', '')
        
        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')
        if not dob_str:
            errors.append('Date of birth is required')
        else:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                if dob >= date.today():
                    errors.append('Date of birth must be in the past')
            except ValueError:
                errors.append('Invalid date of birth format')
        if not address:
            errors.append('Address is required')
        if not city:
            errors.append('City is required')
        if not state or state not in [s[0] for s in US_STATES]:
            errors.append('Please select a valid state')
        if not zipcode or len(zipcode) < 5:
            errors.append('Valid zipcode is required')
        if not camp_session_id:
            errors.append('Please select a camp session')
        else:
            camp_session = CampSession.query.get(camp_session_id)
            if not camp_session:
                errors.append('Selected camp session is invalid')
            elif camp_session.is_full:
                errors.append('Selected camp session is full')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            camp_sessions = CampSession.query.filter(CampSession.date >= date.today()).order_by(CampSession.date).all()
            return render_template('register.html', states=US_STATES, camp_sessions=camp_sessions)
        
        # Store form data in session for waiver page
        session['registration_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob_str,
            'address': address,
            'city': city,
            'state': state,
            'zipcode': zipcode,
            'camp_session_id': int(camp_session_id)
        }
        
        return redirect(url_for('waiver'))
    
    # GET request
    camp_sessions = CampSession.query.filter(CampSession.date >= date.today()).order_by(CampSession.date).all()
    return render_template('register.html', states=US_STATES, camp_sessions=camp_sessions)

@app.route('/waiver', methods=['GET', 'POST'])
def waiver():
    if 'registration_data' not in session:
        flash('Please complete the registration form first', 'error')
        return redirect(url_for('register'))
    
    # Get current date for the template
    current_date = datetime.now().strftime('%m/%d/%Y')
    
    if request.method == 'POST':
        waiver_agreed = request.form.get('waiver_agreed')
        camper_signature = request.form.get('camper_signature', '').strip()
        parent_signature = request.form.get('parent_signature', '').strip()
        
        if not waiver_agreed:
            flash('You must agree to the waiver to complete registration', 'error')
            return render_template('waiver.html', 
                                 registration_data=session['registration_data'],
                                 current_date=current_date)
        
        if not camper_signature:
            flash('Camper signature is required', 'error')
            return render_template('waiver.html', 
                                 registration_data=session['registration_data'],
                                 current_date=current_date)
        
        if not parent_signature:
            flash('Parent/Guardian signature is required', 'error')
            return render_template('waiver.html', 
                                 registration_data=session['registration_data'],
                                 current_date=current_date)
        
        # Save registration to database
        reg_data = session['registration_data']
        registration = Registration(
            first_name=reg_data['first_name'],
            last_name=reg_data['last_name'],
            dob=datetime.strptime(reg_data['dob'], '%Y-%m-%d').date(),
            address=reg_data['address'],
            city=reg_data['city'],
            state=reg_data['state'],
            zipcode=reg_data['zipcode'],
            camp_session_id=reg_data['camp_session_id'],
            waiver_signed=True
        )
        
        # Update camp session enrollment
        camp_session = CampSession.query.get(reg_data['camp_session_id'])
        camp_session.current_enrollment += 1
        
        db.session.add(registration)
        db.session.commit()
        
        # Clear session data
        session.pop('registration_data', None)
        
        flash('Registration completed successfully!', 'success')
        return redirect(url_for('confirmation', registration_id=registration.id))
    
    return render_template('waiver.html', 
                         registration_data=session['registration_data'],
                         current_date=current_date)

@app.route('/confirmation/<int:registration_id>')
def confirmation(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    return render_template('confirmation.html', registration=registration)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'klayko':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    camp_sessions = CampSession.query.order_by(CampSession.date).all()
    registrations = Registration.query.order_by(Registration.registration_date.desc()).all()
    return render_template('admin_dashboard.html', camp_sessions=camp_sessions, registrations=registrations)

@app.route('/admin/add_session', methods=['GET', 'POST'])
@login_required
def add_session():
    if request.method == 'POST':
        date_str = request.form.get('date')
        location = request.form.get('location', '').strip()
        time = request.form.get('time', '').strip()
        price = request.form.get('price')
        max_capacity = request.form.get('max_capacity')
        
        errors = []
        if not date_str:
            errors.append('Date is required')
        if not location:
            errors.append('Location is required')
        if not time:
            errors.append('Time is required')
        if not price:
            errors.append('Price is required')
        if not max_capacity:
            errors.append('Maximum capacity is required')
        
        if not errors:
            try:
                session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                price_float = float(price)
                capacity_int = int(max_capacity)
                
                camp_session = CampSession(
                    date=session_date,
                    location=location,
                    time=time,
                    price=price_float,
                    max_capacity=capacity_int
                )
                
                db.session.add(camp_session)
                db.session.commit()
                
                flash('Camp session added successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            except ValueError as e:
                errors.append('Invalid date, price, or capacity format')
        
        for error in errors:
            flash(error, 'error')
    
    return render_template('add_session.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
