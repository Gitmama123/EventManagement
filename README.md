<h1>🎉 Event Logistics & Schedule Manager </h1>

<h2>A modern Flask-based event management system for handling events, venues, participants, resources, attendance, and scheduling — complete with authentication, role-based access, and a real-time dashboard.</h2>

🚀 Features

🔐 User Authentication & Roles
```
Secure login & logout (Flask-Login)
Role support: Admin, Staff, Viewer
Admin/Staff can create & modify data
Viewer: read-only access
Protected routes for all CRUD operations
```
📅 Event Management
```
Add / Edit / Delete events
Select date, start time, end time
Assign events to venues
Automatic schedule conflict detection
Prevent overlapping events at the same venue
Filter events by date
Event participants management
Attendance tracking (per participant)
```
🏛 Venue Management

```
Add, edit, delete venues
Set venue capacity
View resources assigned to each venue
See how many events scheduled at the venue
Integrated conflict system with event scheduling
```
🔧 Venue Resource Management
(Under Venue Management)

```
Add, edit, delete resources per venue
Track resource quantity
Organized per venue
Ensures better planning & logistics visibility
```

🧑‍🤝‍🧑 Participant Management

```
Add, edit, delete participants
Fields include: name, email, phone, notes
Email validation + error display
Phone number validation (10–15 digits, optional +)
Assign participants to events
Remove participants
Prevent duplicate registrations
Auto-enforce venue capacity
Participant list view per event
```
✔️ Attendance Management

```
Mark attendance for each participant
Options: Present / Absent / Not Marked
Bulk-update or individual update
Attendance stored in event-participant association
Completely integrated with dashboard
```

📊 Dashboard & Analytics

```
Real-time dashboard with:
Total Events
Total Venues
Total Participants
Total Resources
Today’s Attendance Summary
Registered / Present / Absent / Not Marked
Attendance percentage
7-day events bar chart (Chart.js)
Upcoming events (next 14 days)
Quick links to:
Participants per event
Mark Attendance
```

🎨 UI & UX

```
Responsive Bootstrap 5 design
Intuitive navigation bar: Dashboard, Events, Venues, Participants
Clean form layouts with validation highlights
Organized templates: events, venues, participants, auth
Flash messages for success/error/info
Modern color scheme & clean spacing
```
📁 Project Structure

```text
EventManagement/
│── app/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── events/
│   │   │   ├── list.html
│   │   │   ├── add_edit.html
│   │   │   ├── participants.html
│   │   │   └── attendance.html
│   │   ├── venues/
│   │   │   ├── list.html
│   │   │   ├── add_edit.html
│   │   │   ├── resources.html
│   │   │   └── resource_add_edit.html
│   │   ├── participants/
│   │   │   ├── list.html
│   │   │   └── add_edit.html
│   │   └── auth/
│   │       ├── login.html
│   │       └── register.html
│   │
│   └── static/
│
│── instance/
│   └── app.db
│
│── requirements.txt
└── README.md
```
⚙️ Installation & Setup
1️⃣ Clone the Repository
```
git clone https://github.com/Gitmama123/EventManagement.git
```
```
cd EventManagement
```
2️⃣ Create Virtual Environment
```
python -m venv venv
```

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

4️⃣ Initialize the Database
```
python app.py
```

The app will automatically create instance/app.db if it doesn’t exist.

5️⃣ Open in Browser
http://127.0.0.1:5000

🛠 Technologies Used
```
Python 3
Flask
Flask-SQLAlchemy
Flask-WTF & WTForms
Flask-Login
Bootstrap 5
Chart.js
SQLite
```
📜 License

This project is open-source for educational and personal use.
Feel free to modify, extend, and improve it.
