# 📚 LearnVerse - AI-Powered Learning Platform

## 🎓 Overview
LearnVerse is a full-featured online learning platform built with Flask, SQLite, and modern web technologies. It allows students to discover, enroll, and learn from courses while instructors can create and manage content.

## ✨ Features Implemented

### Core Features
| Feature | Status | Priority |
|---------|--------|----------|
| Course Listing | ✅ Done | 1 |
| Course Detail | ✅ Done | 1 |
| Admin Dashboard | ✅ Done | 1 |
| Course CRUD | ✅ Done | 1 |
| Search & Filters | ✅ Done | 1 |
| Admin Search | ✅ Done | 1 |
| Export CSV | ✅ Done | 1 |
| Responsive Design | ✅ Done | 1 |

### Tech Stack
- **Backend**: Flask (Python 3.10+)
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Theme**: Modern SaaS Blue (#2563EB)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git (optional)

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/Preethivel/Capstone-Project.git
cd Capstone-Project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Run application
python app.py