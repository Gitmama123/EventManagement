📘 Event Manager (with User Login System)

A lightweight Flask-based web application for managing events and venues, now enhanced with a secure user authentication system (register/login/logout).
Designed for college event committees, office scheduling, or any small-scale event management workflow.

🚀 Features
✅ User Authentication

Secure registration with hashed passwords

Login / Logout using Flask-Login

Session-based authentication

Unauthorized users are automatically redirected to login

🎯 Event Management

Add events with:

Title

Description

Date

Start & End Time

Venue selection

Edit/Delete events

Auto-detection of venue booking conflicts

Sort events by date and time

🏛 Venue Management

Add/Edit/Delete venues

Store capacity and resources

Prevent deleting venues with linked events

🛡 Access Control

Viewing events/venues → public

Adding/editing/deleting → login required

📂 Project Structure
event_manager/
│── app.py
│── config.py
│── requirements.txt
│── instance/
│     └── app.db
│── app/
     │── __init__.py
     │── auth.py
     │── routes.py
     │── models.py
     │── forms.py
     │── templates/
         │── base.html
         │── auth/
         │     ├── login.html
         │     └── register.html
         │── events/
         │── venues/
     │── static/

🛠 Installation & Setup
1. Create and activate virtual environment
   
```bash
python -m venv venv



source venv/bin/activate        # Mac/Linux



venv\Scripts\activate           # Windows
```

3. Install dependencies
   
```bash
pip install -r requirements.txt
```

5. Run the application
   
```bash
python app.py
```

7. Open your browser

Visit:

```
http://127.0.0.1:5000
```

🔐 Authentication Details

Passwords are hashed using Werkzeug security

User sessions handled by Flask-Login

Login-required protection for:

Adding venues

Adding events

Editing events/venues

Deleting events/venues

🧠 Conflict Checking Logic

Events cannot overlap in the same venue.

Two events conflict if:

start_time < existing_end AND end_time > existing_start


If conflict detected → user gets an error.

🎨 Frontend

Styled with Bootstrap 5

Responsive and clean UI

Navbar updates dynamically based on login state

📦 Dependencies

Main libraries:

Flask
Flask-WTF
Flask-SQLAlchemy
Flask-Login
Werkzeug
