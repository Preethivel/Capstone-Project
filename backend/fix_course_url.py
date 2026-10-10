from database import SessionLocal
from models import Course

db = SessionLocal()
courses = db.query(Course).all()
for c in courses:
    c.course_url = None
db.commit()
print("Done! course_url cleared for all courses")
db.close()