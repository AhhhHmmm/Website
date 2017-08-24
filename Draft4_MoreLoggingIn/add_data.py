from datetime import datetime
from app import db, User, Block, Unit, Lesson, Subject, Question, Part, Response

TODAY = datetime.utcnow()

block_file = 'blocks.txt'
subject_file = 'subjects.txt'
unit_file = 'units.txt'
lesson_file = 'lessons.txt'
question_file = 'questions.txt'
part_file = 'parts.txt'

def add_subjects(subject_file):
	with open(subject_file) as f:
		for line in f:
			line = line.strip()
			subject_name = line
			subject = Subject(subject_name=subject_name)
			db.session.add(subject)
			db.session.commit()

def add_blocks(block_file):
	with open(block_file) as f:
		for line in f:
			line = line.split(',')
			block_number = int(line[0])
			subject_name = line[1].strip()
			subject = Subject.query.filter(Subject.subject_name == subject_name).first()
			block = Block(block_number=block_number, subject=subject)
			db.session.add(block)
			db.session.commit()

def add_units(block_file):
	with open(unit_file) as f:
		for line in f:
			line = line.split(',')
			unit_number = int(line[0])
			title = line[1].strip()
			subject_name = line[2].strip()
			subject = Subject.query.filter(Subject.subject_name == subject_name).first()
			unit = Unit(unit_number=unit_number, title=title, subject=subject)
			db.session.add(unit)
			db.session.commit()

def add_lessons(lesson_file):
	with open(lesson_file) as f:
		for line in f:
			line = line.split(',')
			lesson_number = int(line[0])
			title = line[1].strip()
			date_assigned = TODAY
			available = line[2].strip()
			if available == 'True':
				available = True
			else:
				available = False
			unit_title = line[-1].strip()
			unit = Unit.query.filter(Unit.title == unit_title).first()
			lesson = Lesson(lesson_number=lesson_number, title=title, date_assigned=date_assigned, available=available, unit=unit)
			db.session.add(lesson)
			db.session.commit()

def add_questions(question_file):
	with open(question_file) as f:
		for line in f:
			line = line.split(',')
			number = int(line[0])
			html = line[1].strip()
			lesson_title = line[-1].strip()
			lesson = Lesson.query.filter(Lesson.title == lesson_title).first()
			question = Question(number=number, html=html, lesson=lesson)
			db.session.add(question)
			db.session.commit()



def add_parts(part_file):
	with open(part_file) as f:
		for line in f:
			line = line.split(',')
			part = line[0]
			html = line[1].strip()
			answer = line[2].strip()
			question_id = line[-1].strip()
			part = Part(part=part,html=html,answer=answer,question_id=question_id)
			db.session.add(part)
			db.session.commit()


def add_all():
	add_subjects(subject_file)
	add_blocks(block_file)
	add_units(block_file)
	add_lessons(lesson_file)