# Volleyball Camp Registration System
©Colt McVey@2025
A Flask web application for managing volleyball camp registrations with waiver forms and admin panel.

## Features

- **Registration Form**: Collects camper information including name, DOB, address with US state dropdown
- **Camp Calendar**: Displays available camp sessions with dates, times, locations, and pricing
- **Vacancy Tracking**: Shows available spots and prevents registration when sessions are full
- **Digital Waiver**: Complete waiver and release of liability form with digital signatures
- **SQLite Database**: Stores all registration data locally
- **Admin Panel**: Secure admin interface to manage camp sessions and view registrations
- **Form Validation**: Client and server-side validation for all forms

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Directory Structure

Create the following folder structure:

```
volleyball_camp/
├── app.py
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── index.html
    ├── register.html
    ├── waiver.html
    ├── confirmation.html
    ├── admin_login.html
    ├── admin_dashboard.html
    └── add_session.html
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 4. Admin Access

- **Username**: admin
- **Password**: klayko
- Access admin panel at: `http://localhost:5000/admin/login`

## Usage

### For Users:
1. Visit the home page
2. Click "Register Now"
3. Fill out the registration form
4. Select an available camp session
5. Complete the digital waiver form
6. Receive confirmation

### For Admins:
1. Login to admin panel
2. Add new camp sessions with date, time, location, price, and capacity
3. View all registrations and session enrollment
4. Monitor available spots for each session

## Database

The application uses SQLite database (`volleyball_camp.db`) which will be created automatically when you first run the app. The database includes:

- **CampSession**: Stores camp session details and tracks enrollment
- **Registration**: Stores camper information and waiver status

## Form Validation

The application includes comprehensive validation:
- Required field checking
- Date format validation
- State selection validation
- Zipcode format validation
- Session availability checking
- Waiver agreement verification

## Security Features

- Session-based admin authentication
- CSRF protection with Flask's secret key
- Input sanitization and validation
- SQL injection prevention with SQLAlchemy ORM

## Customization

You can easily customize:
- Camp name and branding in templates
- Waiver text content
- Form fields and validation rules
- Admin credentials (change in app.py)
- Styling with Bootstrap classes

## File Structure

- `app.py`: Main Flask application with routes and database models
- `templates/`: HTML templates using Jinja2
- `requirements.txt`: Python dependencies
- `volleyball_camp.db`: SQLite database (created automatically)

## Notes

- The application automatically creates the database tables on first run
- Session enrollment is automatically updated when registrations are completed
- All dates and times are displayed in user-friendly formats
- The waiver form includes all the specified legal text
