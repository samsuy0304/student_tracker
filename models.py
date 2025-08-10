from flask_sqlalchemy import SQLAlchemy

# shared db object
db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(10))
    citizenship = db.Column(db.String(50))
    intended_major = db.Column(db.String(100))
    entry_semester = db.Column(db.String(20))
    entry_year = db.Column(db.Integer)
    assigned_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD

    # relationship backref for tasks
    tasks = db.relationship('Task', backref='student', cascade='all, delete-orphan', lazy=True)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.Date, nullable=True)