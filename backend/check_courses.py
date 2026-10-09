from database import SessionLocal
from models import Course

db = SessionLocal()
for c in db.query(Course).all():
    print(f'ID:{c.id} Title:{c.title} Price:{c.price} URL:{c.course_url}')
db.close()