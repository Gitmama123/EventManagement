# Event Logistics & Schedule Manager

A Flask-based web application to manage **events**, **venues**, and **venue resources**, with full **user authentication** and a clean Bootstrap UI.

---

## 🚀 Features

### 🔐 User Authentication
- User registration & login
- Protected routes for all CRUD operations
- Access control for editing/deleting entities

### 📅 Event Management
- Add, edit, delete events
- Select date, start time, end time
- Assign events to venues
- Detect & prevent scheduling conflicts
- Filter events by date
- Clean tabular UI for event listings

### 🏛 Venue Management
- Add, edit, delete venues
- Track venue capacity
- View number of resources per venue
- Dedicated page for each venue’s resources

### 🔧 Venue Resource Management
(Under Venue Management)
- Add, edit, delete resources per venue
- Track resource quantity
- Structured Resource model connected to Venue
- Full CRUD interface

### 🎨 UI & UX
- Responsive Bootstrap design
- Unified Navbar (Events, Venues, Login/Logout)
- Flash messages (success/error/info)
- Clean form layouts with validation

---

## 📂 Project Structure

EventManagement/
│
├── app/
│ ├── init.py
│ ├── app.py
│ ├── models.py
│ ├── routes.py
│ ├── auth.py
│ ├── forms.py
│ │
│ ├── templates/
│ │ ├── base.html
│ │ ├── events/
│ │ │ ├── list.html
│ │ │ └── add_edit.html
│ │ ├── venues/
│ │ │ ├── list.html
│ │ │ ├── add_edit.html
│ │ │ ├── resources.html
│ │ │ └── resource_add_edit.html
│ │ └── auth/
│ │ ├── login.html
│ │ └── register.html
│ │
│ └── static/
│
├── instance/
│ └── app.db
│
├── requirements.txt
└── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
gh repo clone Gitmama123/EventManagement
cd EventManagement
```
2️⃣ Create Virtual Environment
```
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```
3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
4️⃣ Initialize the Database
```
python app.py
```
Open your browser:
```
http://127.0.0.1:5000
```
🧪 Usage Flow

Register a new account

Login

Add venues

Add resources under each venue

Add events and assign them to venues

Edit/delete as needed

Filter events by date

🛠 Technologies Used

Python 3

