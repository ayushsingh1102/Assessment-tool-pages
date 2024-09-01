from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/assesment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Added 'type' column for assessment type
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    questions = db.relationship('Question', backref='assessment', lazy=True)  # Relationship with Question

    def __repr__(self):
        return f'<Assessment {self.title}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Type of question (MCQ, Short Answer, etc.)
    options = db.Column(db.Text)  # For MCQ options
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)

    def __repr__(self):
        return f'<Question {self.text}>'

# Ensure tables are created
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    assessments = Assessment.query.all()
    return render_template('index.html', assessments=assessments)

@app.route('/create', methods=['GET', 'POST'])
def create_assessment():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        type = request.form['type']  # Get assessment type from form

        new_assessment = Assessment(title=title, description=description, type=type)
        db.session.add(new_assessment)
        db.session.commit()

        flash('Assessment Created Successfully!')
        return redirect(url_for('index'))

    return render_template('create_assessment.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_assessment(id):
    assessment = Assessment.query.get_or_404(id)

    if request.method == 'POST':
        assessment.title = request.form['title']
        assessment.description = request.form['description']
        assessment.type = request.form['type']  # Update assessment type
        db.session.commit()

        flash('Assessment Updated Successfully!')
        return redirect(url_for('index'))

    return render_template('update_assessment.html', assessment=assessment)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    db.session.delete(assessment)
    db.session.commit()

    flash('Assessment Deleted Successfully!')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    search = request.args.get('search', '')
    filter_by = request.args.get('filter', '')

    query = Assessment.query

    if search:
        query = query.filter(Assessment.title.like(f'%{search}%'))

    if filter_by == 'recent':
        query = query.order_by(Assessment.created_at.desc())
    elif filter_by == 'oldest':
        query = query.order_by(Assessment.created_at.asc())
    elif filter_by == 'completed':
        query = query.filter(Assessment.status == 'completed')  # Assuming status is part of your model
    elif filter_by == 'pending':
        query = query.filter(Assessment.status == 'pending')  # Assuming status is part of your model

    assessments = query.all()

    return render_template('index.html', assessments=assessments)

@app.route('/recent_activities')
def recent_activities():
    recent_activities = [
        {'activity': 'Assessment 1 created', 'date': datetime.utcnow()},
        {'activity': 'Assessment 2 updated', 'date': datetime.utcnow()}
    ]
    return render_template('recent_activities.html', activities=recent_activities)

@app.route('/analytics_summary')
def analytics_summary():
    total_assessments = Assessment.query.count()
    recent_assessments = Assessment.query.filter(Assessment.created_at > datetime.utcnow() - timedelta(days=30)).count()
    
    analytics = {
        'total_assessments': total_assessments,
        'recent_assessments': recent_assessments,
        'assessment_by_month': [
            {'month': 'August', 'count': 10},
            {'month': 'July', 'count': 5}
        ]
    }
    
    return render_template('analytics_summary.html', analytics=analytics)

@app.route('/create_question/<int:assessment_id>', methods=['GET', 'POST'])
def create_question(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)

    if request.method == 'POST':
        text = request.form['text']
        type = request.form['type']
        options = request.form.get('options')  # For MCQ options

        new_question = Question(text=text, type=type, options=options, assessment=assessment)
        db.session.add(new_question)
        db.session.commit()

        flash('Question Added Successfully!')
        return redirect(url_for('index'))

    return render_template('create_question.html', assessment=assessment)
@app.route('/question_bank')
def question_bank():
    # Your logic here
    return render_template('questionbank.html')


if __name__ == '__main__':
    app.run(debug=True)
