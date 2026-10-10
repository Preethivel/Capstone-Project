from database import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()

# Disable foreign key checks and delete all
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.execute(text("DELETE FROM reviews"))
    conn.execute(text("DELETE FROM lesson_completions"))
    conn.execute(text("DELETE FROM payments"))
    conn.execute(text("DELETE FROM enrollments"))
    conn.execute(text("DELETE FROM lessons"))
    conn.execute(text("DELETE FROM modules"))
    conn.execute(text("DELETE FROM courses"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

print("All courses and related data deleted successfully!")
db.close()