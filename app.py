from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_names = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    pizza = db.Column(db.Boolean, default=False)
    pasta = db.Column(db.Boolean, default=False)
    pap_wors = db.Column(db.Boolean, default=False)
    other_food = db.Column(db.Boolean, default=False)
    movies_rating = db.Column(db.Integer)
    radio_rating = db.Column(db.Integer)
    eat_out_rating = db.Column(db.Integer)
    tv_rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < 
               (self.date_of_birth.month, self.date_of_birth.day))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Validate age
    dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
    age = (datetime.now() - dob).days // 365
    if not (5 <= age <= 120):
        return "Age must be between 5 and 120", 400

    # Create survey record
    survey = Survey(
        full_names=request.form['full_names'],
        email=request.form['email'],
        date_of_birth=dob,
        contact_number=request.form['contact'],
        pizza='pizza' in request.form.getlist('food'),
        pasta='pasta' in request.form.getlist('food'),
        pap_wors='pap_wors' in request.form.getlist('food'),
        other_food='other' in request.form.getlist('food'),
        movies_rating=int(request.form['movies']),
        radio_rating=int(request.form['radio']),
        eat_out_rating=int(request.form['eat_out']),
        tv_rating=int(request.form['tv'])
    )
    
    db.session.add(survey)
    db.session.commit()
    return redirect(url_for('results'))

@app.route('/results')
def results():
    surveys = Survey.query.all()
    if not surveys:
        return "No Surveys Available"
    
    # Calculate statistics
    total = len(surveys)
    ages = [s.age() for s in surveys]
    
    return render_template('results.html', 
        total=total,
        avg_age=round(sum(ages) / total, 1),
        oldest=max(ages),
        youngest=min(ages),
        pizza_percent=round(sum(1 for s in surveys if s.pizza) / total * 100, 1),
        pasta_percent=round(sum(1 for s in surveys if s.pasta) / total * 100, 1),
        pap_wors_percent=round(sum(1 for s in surveys if s.pap_wors) / total * 100, 1),
        movies_avg=round(sum(s.movies_rating for s in surveys) / total, 1),
        radio_avg=round(sum(s.radio_rating for s in surveys) / total, 1),
        eat_out_avg=round(sum(s.eat_out_rating for s in surveys) / total, 1),
        tv_avg=round(sum(s.tv_rating for s in surveys) / total, 1)
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)