from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Event, Attendee, User
from flask import session

app = Flask(__name__)

# Local SQLite for development (replace with Azure SQL URI for deployment)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sqladmin:Admin123@eventhorizon-sql-server.database.windows.net:1433/EventPortalDB?driver=ODBC+Driver+17+for+SQL+Server'
app.secret_key = 'secretkey'  # Replace with secure key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/home')
def home():
    from models import Event, Attendee
    events = Event.query.all()

    # Create a dictionary mapping event.id -> number of registrations
    attendee_counts = {
        event.id: Attendee.query.filter_by(event_id=event.id).count()
        for event in events
    }

    return render_template('home.html', events=events, attendee_counts=attendee_counts)

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        data = {
            "name": request.form['name'],
            "date": request.form['date'],
            "description": request.form['description'],
            "location": request.form['location'],
            "capacity": int(request.form['capacity'])
        }
        new_event = Event(**data)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_event.html')

@app.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.name = request.form['name']
        event.date = request.form['date']
        event.description = request.form['description']
        event.location = request.form['location']
        event.capacity = int(request.form['capacity'])
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_event.html', event=event)

@app.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register_attendee(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        attendee = Attendee(name=name, email=email, event_id=event.id)
        db.session.add(attendee)
        db.session.commit()
        return "🎉 Registration successful!"
    return render_template('register_attendee.html', event=event)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(email=email, password=password, role=role).first()
        if user:
            session['user'] = user.email
            session['role'] = user.role
            return redirect(url_for('home'))
        return "Login failed. Check credentials."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        new_user = User(
            email=request.form['email'],
            password=request.form['password'],
            role=request.form['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register_user.html')

@app.route('/attendees')
def view_attendees():
    if 'role' not in session or session['role'] != 'organizer':
        return redirect(url_for('login'))

    from models import Attendee, Event
    attendees = Attendee.query.all()
    events = {e.id: e.name for e in Event.query.all()}
    return render_template('view_attendees.html', attendees=attendees, events=events)

@app.route('/attendees/event/<int:event_id>')
def view_attendees_event(event_id):
    if 'role' not in session or session['role'] != 'organizer':
        return redirect(url_for('login'))

    from models import Attendee, Event
    event = Event.query.get_or_404(event_id)
    attendees = Attendee.query.filter_by(event_id=event_id).all()
    return render_template('view_attendees_event.html', attendees=attendees, event=event)
@app.route('/my-events')
def my_events():
    if 'role' not in session or session['role'] != 'attendee':
        return redirect(url_for('login'))

    from models import Event, Attendee
    user_email = session.get('user')

    # Get all event IDs this attendee registered for
    attendee_records = Attendee.query.filter_by(email=user_email).all()
    event_ids = [a.event_id for a in attendee_records]
    events = Event.query.filter(Event.id.in_(event_ids)).all()

    return render_template('my_events.html', events=events)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
