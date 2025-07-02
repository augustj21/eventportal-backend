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
    events = Event.query.all()
    return render_template('home.html', events=events)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
