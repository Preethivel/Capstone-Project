# Enhancement Proposal
## Feature: AI-Powered Course Assistant & Personalized Recommendations
## Problem
Learners struggle to find relevant courses and get quick answers about course content.
## Solution
Integrate Gemini AI to power a chat assistant and personalize course recommendations based on enrollment history.
## Tech Choice
Google Gemini API (already integrated), enrollment table for domain preference extraction.
## Implementation Plan
1. Update recommendation endpoint to use enrollment-based domain filtering
2. Surface AI assistant in learner dashboard
3. Add unit tests for recommendation service
## Success Criteria
- Recommendations change based on user's enrolled domains
- AI assistant responds to course-related queries within 3 seconds
