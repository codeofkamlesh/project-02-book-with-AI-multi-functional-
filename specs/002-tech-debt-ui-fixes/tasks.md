# Implementation Tasks: Technical Debt & UI Bug Fixes for Robotics Textbook

**Feature**: 002-tech-debt-ui-fixes
**Created**: 2025-12-17
**Status**: Draft

## Dependencies

- User Story 3 (Urdu Widget DOM Access) depends on User Story 2 (Urdu Translation API) for proper API integration
- CSS standardization can be done in parallel with other tasks

## Parallel Execution Opportunities

- Backend audit and frontend React fixes can be done in parallel
- CSS standardization can be done independently
- DOM lifecycle fix can be done in parallel with other tasks

## Implementation Strategy

MVP approach: Focus on User Story 1 (PersonalizeButton) and User Story 2 (Urdu Translation API) first, as these are P1 priority items. Then implement User Stories 3 and 4 in subsequent phases.

## Phase 1: Setup

- [ ] T001 Create feature branch 002-tech-debt-ui-fixes and ensure proper Git configuration
- [ ] T002 Set up development environment with required dependencies
- [ ] T003 Document current system architecture and component relationships

## Phase 2: Foundational

- [ ] T004 Locate and examine the FastAPI main.py file structure
- [ ] T005 Identify all existing translation-related API routes
- [ ] T006 Locate all frontend translation component files for analysis

## Phase 3: [US1] PersonalizeButton Renders Without Warnings

**Goal**: Eliminate React hydration warning "non-boolean attribute jsx" in PersonalizeButton.

**Independent Test**: PersonalizeButton component renders without React hydration warnings in the console.

- [ ] T007 [P] [US1] Locate PersonalizeButton.jsx component in src/components/personalize/PersonalizeButton.jsx
- [ ] T008 [US1] Identify jsx={true} or jsx prop causing the "non-boolean attribute" warning
- [X] T009 [US1] Remove jsx={true} or jsx prop from HTML tags in PersonalizeButton.jsx
- [ ] T010 [US1] Verify styled-jsx configuration in docusaurus.config.js if used
- [ ] T011 [US1] Test PersonalizeButton component to ensure no React hydration warnings

## Phase 4: [US2] Urdu Translation API Functions Properly

**Goal**: Fix Urdu translation "Not Found" error by correcting the API route in the backend.

**Independent Test**: Urdu translation API returns successful responses (not 404) when called.

- [ ] T012 [P] [US2] Verify the FastAPI main.py file and locate translation POST route
- [ ] T013 [US2] Check if translation endpoint exists and is named correctly (e.g., /translate, /api/v1/translate)
- [ ] T014 [US2] Verify backend endpoint matches frontend call in any UrduTranslator components
- [ ] T015 [US2] Add missing API route prefix if required (e.g., /api/v1/translate)
- [ ] T016 [US2] Test backend endpoint with curl command to verify 200 OK response
- [ ] T017 [US2] Document correct endpoint path for frontend integration

## Phase 5: [US3] Urdu Widget Finds DOM Elements Properly

**Goal**: Ensure the Urdu widget correctly finds DOM element using React refs or Docusaurus lifecycle hooks instead of direct DOM manipulation.

**Independent Test**: Urdu widget uses React refs or lifecycle hooks instead of direct DOM manipulation.

- [X] T018 [P] [US3] Locate translate-widget.js component for analysis
- [X] T019 [US3] Identify all document.getElementById calls in translate-widget.js
- [X] T020 [US3] Refactor translate-widget.js to wrap button detection in window.addEventListener('load')
- [X] T021 [US3] Alternatively, move logic into useEffect hook if part of React component
- [X] T022 [US3] Replace direct DOM manipulation with React useRef approach where applicable
- [X] T023 [US3] Test widget functionality after refactoring to ensure proper DOM access

## Phase 6: [US4] CSS Properties Validate Correctly

**Goal**: Standardize CSS to remove "Unknown property" warnings.

**Independent Test**: Browser console shows zero "Dropped property" CSS warnings.

- [X] T024 [P] [US4] Locate styles.css file for CSS standardization
- [X] T025 [US4] Identify all CSS properties causing "Unknown property" warnings
- [X] T026 [US4] Replace line-clamp: 14 with standard-compliant properties:
  ```css
  display: -webkit-box;
  -webkit-line-clamp: 14;
  -webkit-box-orient: vertical;
  overflow: hidden;
  ```
- [X] T027 [US4] Research and replace other invalid CSS properties with standard-compliant alternatives
- [X] T028 [US4] Apply proper vendor prefixes where needed for browser compatibility
- [X] T029 [US4] Test CSS changes to ensure no visual regressions

## Phase 7: Polish & Integration Testing

**Goal**: Verify all fixes work together without regressions.

- [X] T030 [P] Test Urdu translation functionality end-to-end with updated backend
- [X] T031 Verify personalization features work correctly after PersonalizeButton fix
- [X] T032 Confirm no new console errors or warnings after all changes
- [X] T033 Re-run curl commands to confirm all API endpoints return 200 OK responses
- [X] T034 Verify browser console shows zero "Dropped property" warnings after CSS changes
- [X] T035 Final integration test of all components working together
- [X] T036 Document any remaining issues or improvements for future work