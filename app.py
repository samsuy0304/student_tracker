from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Student, Task
from datetime import datetime
import os

# App setup
app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize db
db.init_app(app)
with app.app_context():
    db.create_all()

# ---------- Routes ----------
@app.route('/')
def dashboard():
    # students grouped/sorted as before, tasks combined for dashboard
    students = Student.query.order_by(
        Student.entry_year.desc().nullslast(),
        Student.entry_semester.asc().nullsfirst(),
        Student.assigned_date.desc().nullslast()
    ).all()
    all_tasks = Task.query.order_by(Task.deadline.asc().nulls_last()).all()
    return render_template('dashboard.html', students=students, all_tasks=all_tasks)

@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    # tasks will be available via student.tasks
    return render_template('student_detail.html', student=student)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # gather and validate minimal fields
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        assigned_date = request.form['assigned_date']

        if not first_name or not last_name or not assigned_date:
            # naive validation — in production provide better UX
            return "Missing required fields", 400

        student = Student(
            first_name=first_name,
            last_name=last_name,
            dob=request.form.get('dob') or None,
            citizenship=request.form.get('citizenship') or None,
            intended_major=request.form.get('intended_major') or None,
            entry_semester=request.form.get('entry_semester') or None,
            entry_year=request.form.get('entry_year') or None,
            assigned_date=assigned_date
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_student.html')

# ---------- Task endpoints ----------
@app.route('/student/<int:student_id>/add_task', methods=['POST'])
def add_task(student_id):
    student = Student.query.get_or_404(student_id)
    description = request.form.get('description', '').strip()
    deadline_str = request.form.get('deadline')
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
    if not description:
        return jsonify({'success': False, 'error': 'Empty description'}), 400

    t = Task(
        student_id=student.id,
        description=description,
        completed=False,
        deadline=deadline
        
    )
    db.session.add(t)
    db.session.commit()
    # if request is AJAX, return JSON; otherwise redirect back
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'task': {'id': t.id, 'description': t.description, 'completed': t.completed}})
    return redirect(url_for('student_detail', id=student_id))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    t = Task.query.get_or_404(task_id)
    t.completed = not t.completed
    db.session.commit()
    return jsonify({'success': True, 'completed': t.completed})

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    try:
        t = Task.query.get(task_id)
        if t is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        db.session.delete(t)
        db.session.commit()
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        # rollback to keep DB session healthy
        db.session.rollback()
        # log the exception so you can inspect server logs
        app.logger.exception("Failed to delete task %s", task_id)
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- Utilities / static simple endpoints ----------
@app.route('/task/<int:task_id>/edit', methods=['POST'])
def edit_task(task_id):
    # optional: support renaming tasks inline
    t = Task.query.get_or_404(task_id)
    desc = request.form.get('description', '').strip()
    if not desc:
        return jsonify({'success': False, 'error': 'Empty description'}), 400
    t.description = desc
    db.session.commit()
    return jsonify({'success': True, 'description': t.description})

if __name__ == '__main__':
    app.run(debug=True)