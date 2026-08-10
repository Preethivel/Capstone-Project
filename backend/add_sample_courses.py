from app import app, db
from models import Course

def add_sample_courses():
    with app.app_context():
        # Clear existing courses first
        db.session.query(Course).delete()
        db.session.commit()
        
        courses = [
            # ===== ON-PLATFORM COURSES (No course_url) =====
            Course(
                title='Python for Beginners',
                description='Learn Python programming from scratch with hands-on projects and real-world examples. Perfect for absolute beginners!',
                domain='Programming',
                level='Beginner',
                price=0,
                instructor='John Doe',
                rating=4.8,
                students=1250,
                status='approved',
                course_url=None  # ← On-platform course
            ),
            Course(
                title='Data Science Fundamentals',
                description='Master data analysis, visualization, and statistical modeling using Python, Pandas, and Matplotlib.',
                domain='Data Science',
                level='Beginner',
                price=0,
                instructor='Dr. Marie Curie',
                rating=4.6,
                students=3200,
                status='approved',
                course_url=None  # ← On-platform course
            ),
            
            # ===== EXTERNAL COURSES (With course_url) =====
            Course(
                title='Advanced Machine Learning with Python',
                description='Master machine learning algorithms including neural networks, random forests, and gradient boosting.',
                domain='AI & ML',
                level='Advanced',
                price=99.99,
                instructor='Dr. Sarah Johnson',
                rating=4.9,
                students=850,
                status='approved',
                course_url='https://www.coursera.org/learn/machine-learning'
            ),
            Course(
                title='Full Stack Web Development',
                description='Build complete web applications using Python, Flask, React, and PostgreSQL.',
                domain='Web Development',
                level='Intermediate',
                price=79.99,
                instructor='Jane Smith',
                rating=4.7,
                students=2100,
                status='approved',
                course_url='https://www.freecodecamp.org/learn'
            ),
            Course(
                title='Cybersecurity Essentials',
                description='Learn network security, ethical hacking, and security best practices.',
                domain='Cybersecurity',
                level='Intermediate',
                price=49.99,
                instructor='Kevin Mitnick',
                rating=4.8,
                students=950,
                status='approved',
                course_url='https://www.cybrary.it/'
            ),
            Course(
                title='Cloud Computing with AWS',
                description='Master AWS cloud services including EC2, S3, Lambda, and RDS.',
                domain='Cloud Computing',
                level='Intermediate',
                price=89.99,
                instructor='Jeff Bezos',
                rating=4.7,
                students=1400,
                status='approved',
                course_url='https://aws.amazon.com/training/'
            ),
            Course(
                title='DevOps with Docker & Kubernetes',
                description='Learn containerization, CI/CD pipelines, and infrastructure automation.',
                domain='DevOps',
                level='Advanced',
                price=69.99,
                instructor='James Docker',
                rating=4.5,
                students=680,
                status='approved',
                course_url='https://kubernetes.io/docs/tutorials/'
            ),
            Course(
                title='React Native Mobile Development',
                description='Build cross-platform mobile apps for iOS and Android using React Native.',
                domain='Mobile Development',
                level='Intermediate',
                price=59.99,
                instructor='Mark Zuckerberg',
                rating=4.4,
                students=1100,
                status='approved',
                course_url='https://reactnative.dev/docs/getting-started'
            )
        ]
        
        for course in courses:
            db.session.add(course)
        db.session.commit()
        
        print("✅ Added 8 sample courses!")
        print("   - 2 On-Platform courses (Python, Data Science)")
        print("   - 6 External courses (with links)")

if __name__ == '__main__':
    add_sample_courses()