from database import SessionLocal
from models import Course

db = SessionLocal()
for c in db.query(Course).all():
    c.course_url = None
db.commit()
print("Done! course_url cleared for all courses")
db.close()