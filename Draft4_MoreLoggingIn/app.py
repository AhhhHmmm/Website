from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'


# Database stuff
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Users/admin/desktop/programming/Project_1_Answer_System/Draft4_MoreLoggingIn/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Bootstrap(app)

# login stuff
login_manager = LoginManager()
login_manager.init_app(app)

# The below gives the page redirect if a non-logged in user tries to access a login restricted page. (so the below redirects to /login)
login_manager.login_view = 'login'

# Include UserMixin for flask_login object
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	account_type = db.Column(db.String(20)) # either 'Student' or 'Teacher'
	password = db.Column(db.String(100))
	first_name = db.Column(db.String(40))
	last_name = db.Column(db.String(40))
	# Foreign Keys
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	block_id = db.Column(db.Integer, db.ForeignKey('block.id'))
	# Back Reference
	responses = db.relationship('Response', backref='user', lazy='dynamic')

# We need to reference each unit with a subject so that only A2 stuff appears for A2 students etc..

class Subject(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	subject_name = db.Column(db.String(40), unique=True)
	# Back Reference
	blocks = db.relationship('Block', backref='subject', lazy='dynamic')
	users = db.relationship('User', backref='subject', lazy='dynamic')
	units = db.relationship('Unit', backref='subject', lazy='dynamic')

class Block(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	block_number = db.Column(db.Integer)
	# Foreign Keys
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	# Back Reference
	users = db.relationship('User', backref='block', lazy='dynamic')

# One to Many, one Unit has one lesson
# One lesson has many questions
# One question has many parts

class Unit(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	unit_number = db.Column(db.Integer)
	title = db.Column(db.String(40))
	# Foreign Keys
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
	# Back reference
	lessons = db.relationship('Lesson', backref='unit', lazy='dynamic')

# Going to need to insert a "Subject" model - necessary so correct dashboard displays.
# May need to foreign key with user.

class Lesson(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lesson_number = db.Column(db.Integer)
	title = db.Column(db.String(40))
	date_assigned = db.Column(db.DateTime)
	available = db.Column(db.Boolean)
	# Foreign Keys
	unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
	# Back reference
	questions = db.relationship('Question', backref='lesson', lazy='dynamic')


class Question(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	html = db.Column(db.String)
	# Foreign Keys
	lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
	# Back reference
	parts = db.relationship('Part', backref='question', lazy='dynamic')


class Part(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	part = db.Column(db.String(1))
	html = db.Column(db.String)
	answer = db.Column(db.String)
	# Foreign Keys
	question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
	# Back reference
	responses = db.relationship('Response', backref='part', lazy='dynamic')

class Response(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	response = db.Column(db.String(30))
	correct = db.Column(db.Boolean)
	tries_used = db.Column(db.Integer)
	last_attempt_time = db.Column(db.DateTime)
	# Foreign Keys
	part_id = db.Column(db.Integer, db.ForeignKey('part.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Still need to figure out how to track remaining tries and individual data.

# Form Stuff
class LoginForm(FlaskForm):
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	
class SignUpForm(FlaskForm):
	first_name = StringField(label='First Name', validators=[InputRequired(), Length(max=40)])
	last_name = StringField(label='Last Name', validators=[InputRequired(), Length(max=40)])
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	subject = SelectField(label='Subject', validators=[InputRequired()], choices=[('alg2','Algebra 2'), ('apcsp','AP Computer Science Principles')])
	block = SelectField(label='Block', validators=[InputRequired()], choices=[('3',3),('5',5)])

class CreateUserForm(FlaskForm):
	first_name = StringField(label='First Name', validators=[InputRequired(), Length(max=40)])
	last_name = StringField(label='Last Name', validators=[InputRequired(), Length(max=40)])
	email = StringField(label='Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=80)])
	subject = SelectField(label='Subject', validators=[InputRequired()], choices=[('alg2','Algebra 2'), ('apcsp','AP Computer Science Principles')])
	block = SelectField(label='Block', validators=[InputRequired()], choices=[('3',3),('5',5)])
	account_type = SelectField(label='Account Type', validators=[InputRequired()], choices=[('Admin','Admin'),('Student','Student')])



# The route below is linked to when a user logs in. Searches the database by ID and gets user info
# After logging in the user, all user data from the User table should be accessible by using 'current_user.PROPERTY'.
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

# Format url like /alg2/u2/l1
# Format url like /apcsp/...
@app.route('/assignment/<subject>/<unit>/<lesson>', methods=['GET', 'POST'])
@login_required
def assignment(subject, unit, lesson):
	if subject == 'alg2':
		subject_name = 'Algebra 2'
	elif subject == 'apcsp':
		subject_name = 'AP Computer Science Principles'
	else: 
		return redirect(url_for('dashboard'))

	unit_number = int(unit[1:])
	lesson_number = int(lesson[1:])

	subject = Subject.query.filter(Subject.subject_name == subject_name).first()
	unit = subject.units.filter(Unit.unit_number == unit_number).first()
	lesson = unit.lessons.filter(Lesson.lesson_number == lesson_number).first()
	questions = lesson.questions.all()

	# I need to provide more error handling here - like what if student is messing around with url and unit/lesson do not exist?
	# Also need to block access for unit/lesson that are 'not available', so need to check if lesson is available before students allowed to access

	user_class = subject = Subject.query.get(int(current_user.subject_id)).subject_name
	if user_class == subject_name:
		return render_template('assignment.html', questions=questions, unit=unit, lesson=lesson)
	else:
		return redirect(url_for('dashboard'))

@app.route('/check', methods=['POST'])
@login_required
def check():

	answer = request.form['answer']
	part_id = request.form['part_id']
	user_id = request.form['user_id']
	now = datetime.utcnow()

	part = Part.query.get(int(part_id))

	if answer == part.answer:
		correct = True
	else:
		correct = False

	response = Response.query.filter(Response.part_id == part.id).filter(Response.user_id == current_user.id).first()

	if response:
		response.response = answer
		response.last_attempt_time = now
		response.correct = correct
		response.tries_used += 1
	else:
		response = Response(response=answer, tries_used=1, last_attempt_time=now, correct=correct, part_id=part.id, user_id=current_user.id)
		db.session.add(response)

	db.session.commit()

	return jsonify({'correct' : correct})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignUpForm()

	if form.validate_on_submit():
		if form.subject.data == 'alg2':
			subject_name = 'Algebra 2'
		elif form.subject.data == 'apcsp':
			subject_name = 'AP Computer Science Principles'
		else: 
			return 'Error'

		subject = Subject.query.filter(Subject.subject_name == subject_name).first()

		hashed_password = generate_password_hash(form.password.data)
		block = Block.query.filter(Block.block_number == form.block.data).first()
		new_user = User(email=form.email.data, password=hashed_password, subject=subject, block=block, account_type='Student', first_name=form.first_name.data, last_name=form.last_name.data)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('dashboard'))

	return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				# below logs in the user to the flask user extension
				login_user(user)
				# sends the logged in user to the dashboard
				return redirect(url_for('dashboard'))

	return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
	if current_user.account_type == 'Admin':
		return render_template('admin_dashboard.html')
	else:
		subject = Subject.query.get(int(current_user.subject_id))
		subject_name = subject.subject_name
		units = subject.units.all()
		return render_template('dashboard.html', units=units, subject_name=subject_name)



# made but not tested:

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
	# Only Admins should be able to create users.
	if current_user.account_type == 'Admin':
		form = CreateUserForm()

		# If the form is submitted = i.e. the method is 'POST'
		if form.validate_on_submit():
			if form.subject.data == 'alg2':
				subject_name = 'Algebra 2'
			elif form.subject.data == 'apcsp':
				subject_name = 'AP Computer Science Principles'
			else: 
				return 'Error'

			subject = Subject.query.filter(Subject.subject_name == subject_name).first()

			hashed_password = generate_password_hash(form.password.data)
			block = Block.query.filter(Block.block_number == form.block.data).first()
			account_type = form.account_type.data
			new_user = User(email=form.email.data, password=hashed_password, subject=subject, block=block, account_type=account_type, first_name=form.first_name.data, last_name=form.last_name.data)
			db.session.add(new_user)
			db.session.commit()
			return redirect(url_for('create_user'))

		# This happens if the method is 'GET'
		return render_template('create_user.html', form=form)

	# Non-admin users are redirected if they try to access but should not be able to.
	else: 
		return render_template(url_for('dashboard'))

@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
# Only Admins should be able to create users.
	if current_user.account_type == 'Admin':
		class DeleteUserForm(FlaskForm):
			# Takes in student_list which is a tuple
			all_students = User.query.filter(User.account_type == 'Student').all()
			student_list = []
			for student in all_students:
				student_list += [(str(student.id), student.first_name + ' ' + student.last_name)]

			to_delete_student = SelectField(label='Student to Delete:', validators=[InputRequired()], choices=student_list)

		# test_html = '<ul>\n'
		# for student in student.list:
		# 	test_html += '<li>{}</li>'.format(student.first_name)

		form = DeleteUserForm()

		# If the form is submitted = i.e. the method is 'POST'
		if form.validate_on_submit():
			student = User.query.get(int(form.to_delete_student.data))
			db.session.delete(student)
			db.session.commit()
			return redirect(url_for('delete_user'))
			# return render_template('delete_user.html', form=form)

		# This happens if the method is 'GET'
		return render_template('delete_user.html', form=form)

	# Non-admin users are redirected if they try to access but should not be able to.
	else: 
		return render_template(url_for('dashboard'))

@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
# Only Admins should be able to create users.
	if current_user.account_type == 'Admin':
		class ResetPasswordForm(FlaskForm):
			# Takes in student_list which is a tuple
			all_students = User.query.filter(User.account_type == 'Student').all()
			student_list = []
			for student in all_students:
				student_list += [(str(student.id), student.first_name + ' ' + student.last_name)]

			reset_password_student = SelectField(label='Reset password of:', validators=[InputRequired()], choices=student_list)

		# test_html = '<ul>\n'
		# for student in student.list:
		# 	test_html += '<li>{}</li>'.format(student.first_name)

		form = ResetPasswordForm()

		# If the form is submitted = i.e. the method is 'POST'
		if form.validate_on_submit():
			student = User.query.get(int(form.reset_password_student.data))
			hashed_password = generate_password_hash('password')
			student.password = hashed_password
			db.session.commit()
			return redirect(url_for('reset_password'))
			# return render_template('reset_password.html', form=form)

		# This happens if the method is 'GET'
		return render_template('reset_password.html', form=form)

	# Non-admin users are redirected if they try to access but should not be able to.
	else: 
		return render_template(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
	logout_user() # this is a method that was imported from Flask-Login
	return redirect(url_for('login'))



if __name__ == "__main__":
	app.run(debug=True)