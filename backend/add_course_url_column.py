from app import app, db
from models import Course
import sqlite3
import os

def add_course_url_column():
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'learnverse.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found at:", db_path)
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(courses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'course_url' in columns:
            print("✅ 'course_url' column already exists!")
            conn.close()
            return
        
        # Add the column
        cursor.execute("ALTER TABLE courses ADD COLUMN course_url VARCHAR(500)")
        conn.commit()
        print("✅ Added 'course_url' column to courses table!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_course_url_column()