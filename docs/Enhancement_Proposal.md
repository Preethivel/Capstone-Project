# Enhancement Proposal: LearnVerse AI Learning Assistant

## Goal
Add a focused assistant that explains course recommendations and helps a learner choose the next lesson using existing course metadata and progress.

## Existing foundation
LearnVerse already stores course domains, levels, enrollments, lesson completion, and recommendation data. The assistant can use these signals without introducing API keys or a new provider dependency.

## Proposed design
- Add an `AIRecommendationService` interface under `backend/services/`.
- Keep a deterministic local implementation based on enrolled domains, incomplete lessons, level, and popularity.
- Expose the feature through `/api/recommendations/next`.
- Add an optional provider implementation later, configured only through environment variables.
- Show recommendation explanations in the learner dashboard.

## Safety and scope
No secrets are placed in source code. The first implementation remains deterministic and testable. External model access is optional and isolated behind the service interface.

## Validation
Test recommendation ranking, excluded completed courses, authenticated access, and fallback behavior when a learner has no history.
