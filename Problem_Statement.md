# Problem Statement

## 1. Title
LearnVerse - AI-Powered Online Learning Platform

## 2. Domain
EdTech / Online Learning

## 3. Who is the user? (2-3 user types, with roles)
- **Learner**: Browses courses, enrolls, tracks progress, earns XP and badges
- **Instructor**: Creates courses, adds modules and lessons, tracks student enrollments
- **Admin**: Manages courses, users, and platform content

## 4. What problem are we solving? (3-5 sentences, real-life example)
Students and professionals face overwhelming choices when trying to learn new skills online. Courses are scattered across multiple platforms like Coursera, Udemy, and freeCodeCamp, making it difficult to find the right course. Users waste time visiting different websites to compare prices, check ratings, and read reviews. There is no centralized platform to discover, compare, and access courses from various providers in one place. This leads to decision fatigue, wasted time, and reduced learning motivation.

## 5. Proposed Solution (what the application will do, feature-wise)
LearnVerse is a unified learning platform that provides:
- Course discovery with advanced search and filters
- AI-powered personalized recommendations based on enrolled courses
- Free and paid course enrollment with a demo payment flow
- Progress tracking with XP points and completion percentages
- Instructor tools to create and manage courses with modules and lessons
- Admin panel for complete platform management
- Role-based access for Learners, Instructors, and Admins
- External course links with provider badges

## 6. Core Entities / Database Tables (list all, minimum 5)
1. **User** - Platform users (learners, instructors, admins) with roles
2. **Course** - Available courses with title, description, domain, level, price
3. **Module** - Modules within a course for structured learning
4. **Lesson** - Individual lessons within a module with video/content
5. **Enrollment** - Tracks which user enrolled in which course with progress
6. **LessonCompletion** - Tracks which lessons a user has completed
7. **Payment** - Payment records for paid course enrollments
8. **Review** - User reviews and ratings for courses

## 7. User Roles & Permissions (minimum 2 distinct roles)
| Role | Permissions |
|------|-------------|
| **Learner** | Browse courses, view details, enroll (free/paid), track progress, write reviews, view dashboard |
| **Instructor** | Create and manage courses, add modules/lessons, view student enrollments, track revenue |
| **Admin** | Manage all courses (add/edit/delete), manage users, platform control |

## 8. Success Criteria (e.g. 'a user should be able to book an appointment in under 1 minute')
- A learner should be able to discover and enroll in a course within 1 minute
- A learner should see personalized AI recommendations after enrolling in at least one course
- An instructor should be able to create and publish a course in under 5 minutes
- The platform should support at least 8 courses across 6+ domains
- Progress tracking should update in real-time with completion percentage
- 3 user roles should work seamlessly with role-based navigation

## 9. Out of Scope (clearly list what you will NOT build, to avoid over-commitment)
- Live video streaming or video hosting (YouTube embed only)
- Mobile apps (web-only for MVP)
- Production payment gateway (manual/demo only)
- Email/SMS notifications
- Certificate generation (future enhancement)
- Advanced analytics and reporting
- Social features (discussions, forums, direct messaging)

## 10. Chosen Track
**Python (Flask)** - Using Flask with SQLAlchemy ORM and SQLite database