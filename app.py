from app import create_app, db
from app.models import User, Venue, Event
import os

app = create_app()

if __name__ == '__main__':
    os.makedirs('instance', exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
