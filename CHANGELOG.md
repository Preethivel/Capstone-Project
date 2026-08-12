# Changelog

## [1.0.0] - 2026-08-11

### Added - MVP (Review I)
- Complete user authentication (Signup/Login/Logout)
- 3 user roles: Learner, Instructor, Admin
- Course management with CRUD operations
- Free and paid course enrollment with demo payment flow
- AI-based course recommendations using content-based filtering
- Instructor dashboard for creating courses, modules, and lessons
- Admin panel for managing all courses
- 8 database tables with proper relationships
- Clean responsive UI with Modern SaaS Blue theme
- Password visibility toggle on login/signup
- External course links with provider badges
- Search and filter functionality for courses
- Student dashboard with progress tracking and XP points
- Profile page for user management

### Technical
- Flask backend with SQLite database
- SQLAlchemy ORM
- HTML/CSS/JS frontend with Jinja2 templates
- 9+ GitHub commits following Conventional Commits format
- Modular folder structure (backend/frontend separation)

### Documentation
- Problem_Statement.md with all 10 sections
- README.md with setup instructions
- Architecture, ER, and Class/Module diagrams
- .gitignore, .env.example, LICENSE

### Upcoming (Review II - Day 41)
- JWT authentication replacing session auth
- Cloud deployment on Render
- Unit tests with pytest
- CI/CD with GitHub Actions
- Swagger/OpenAPI documentation
- Live public URL