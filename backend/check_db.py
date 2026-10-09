from database import SessionLocal
from models import Course

db = SessionLocal()
courses = db.query(Course).all()
for c in courses:
    c.status = "approved"
db.commit()
print("All courses updated to approved!")
db.close()