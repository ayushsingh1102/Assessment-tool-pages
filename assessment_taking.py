from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/assessment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Models


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    instructions = db.Column(db.Text)
    duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    question_text = db.Column(db.Text)
    question_type = db.Column(db.Enum('multiple_choice', 'short_answer'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class StudentAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    status = db.Column(db.Enum('in_progress', 'submitted'))
    started_at = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_assessment_id = db.Column(db.Integer, db.ForeignKey('student_assessment.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    response_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
# Context for table creation
with app.app_context():
    db.create_all()
# Routes

@app.route('/')
def index():
    assessment = Assessment.query.first()  # Get the first assessment
    if assessment is None:
        return "No assessments found", 404
    return render_template('assessment_take.html', assessment=assessment)
@app.route('/add_sample_data')
def add_sample_data():
    # Check if the table is empty
    if not Assessment.query.first():
        # Create sample assessments
        sample_assessment = Assessment(
            title='Sample Assessment 1',
            instructions='Please complete all questions within the given time.',
            duration=60  # duration in minutes
        )
        db.session.add(sample_assessment)
        db.session.commit()
        return "Sample assessment added successfully!"
    else:
        return "Sample data already exists."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route('/take_assessment/<int:assessment_id>', methods=['GET', 'POST'])
def take_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    student_id = 1  # Example student ID, replace with actual logic
    student_assessment = StudentAssessment.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()

    if not student_assessment:
        student_assessment = StudentAssessment(student_id=student_id, assessment_id=assessment_id, status='in_progress', started_at=datetime.now())
        db.session.add(student_assessment)
        db.session.commit()

    if request.method == 'POST':
        responses = request.form.getlist('response')
        question_ids = request.form.getlist('question_id')

        for i in range(len(responses)):
            response = Response(student_assessment_id=student_assessment.id, question_id=question_ids[i], response_text=responses[i])
            db.session.add(response)
        
        if 'submit' in request.form:
            student_assessment.status = 'submitted'
            student_assessment.submitted_at = datetime.now()
        
        db.session.commit()
        flash('Progress saved!' if 'save' in request.form else 'Assessment submitted!')
        return redirect(url_for('index'))

    questions = Question.query.filter_by(assessment_id=assessment.id).all()
    return render_template('assessment_take.html', assessment=assessment, questions=questions, student_assessment=student_assessment)

if __name__ == '__main__':
    app.run(debug=True)
