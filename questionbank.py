from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/question_bank'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    questions = db.relationship('Question', backref='category', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    tags = db.relationship('Tag', secondary='question_tag', backref=db.backref('questions', lazy='dynamic'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class QuestionTag(db.Model):
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

# Routes

@app.route('/')
def index():
    questions = Question.query.all()
    categories = Category.query.all()
    tags = Tag.query.all()
    print(f"Categories: {categories}")
    return render_template('questionbank.html', questions=questions, categories=categories, tags=tags)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@app.route('/question/add', methods=['POST'])
def add_question():
    title = request.form.get('title')
    content = request.form.get('content')
    difficulty = request.form.get('difficulty')
    category_id = request.form.get('category')
    tag_names = request.form.get('tags').split(',')

    # Check if the required fields are provided
    if not title or not content or not difficulty or not category_id:
        return "All fields are required", 400
    
    # Create the question object
    question = Question(title=title, content=content, difficulty=difficulty, category_id=category_id)
    db.session.add(question)
    db.session.commit()

    # Process tags
    for name in tag_names:
        name = name.strip()  # Remove any leading or trailing whitespace
        if name:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            question.tags.append(tag)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/question/edit/<int:id>', methods=['POST'])
def edit_question(id):
    question = Question.query.get(id)
    title = request.form.get('title')
    content = request.form.get('content')
    difficulty = request.form.get('difficulty')
    category_id = request.form.get('category')
    tag_names = request.form.get('tags').split(',')

    # Ensure required fields are provided
    if not title or not content or not difficulty or not category_id:
        return "All fields are required", 400

    # Update the question object
    question.title = title
    question.content = content
    question.difficulty = difficulty
    question.category_id = category_id
    db.session.commit()

    # Update tags
    question.tags = []
    for name in tag_names:
        name = name.strip()
        if name:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            question.tags.append(tag)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/question/delete/<int:id>', methods=['POST'])
def delete_question(id):
    question = Question.query.get(id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/import_questions', methods=['POST'])
def import_questions():
    # Implement import logic here
    return redirect(url_for('index'))

@app.route('/export_questions', methods=['GET'])
def export_questions():
    # Implement export logic here
    return redirect(url_for('index'))

@app.route('/api/categories', methods=['GET'])
def api_categories():
    categories = Category.query.all()
    return jsonify([{'id': category.id, 'name': category.name} for category in categories])

if __name__ == '__main__':
    app.run(debug=True)
