---
id: 4
title: "Tech Debt Fix Tasks Breakdown"
stage: tasks
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: tech-debt-ui-fixes
branch: 002-tech-debt-ui-fixes
user: user
command: "/sp.tasks

1. **Backend Audit:** Verify the FastAPI `main.py` file. Locate the translation POST route. If it's missing or named incorrectly, fix it to match the frontend call in `UrduTranslator.tsx`.
2. **Frontend React Fix:** Open `src/components/personalize/PersonalizeButton.jsx`. Remove `jsx={true}` or `jsx` from any HTML tags. If using styled-jsx, ensure it is configured correctly in docusaurus.config.js.
3. **DOM Lifecycle Fix:** Refactor `src/components/translate-widget.js`. Instead of running raw script logic, wrap the button detection in a `window.addEventListener('load')` or move the logic into the `UrduTranslator` component's `useEffect`.
4. **CSS Standardization:** Edit `styles.css`. Replace `line-clamp: 14` with:
   ```css
   display: -webkit-box;
   -webkit-line-clamp: 14;
   -webkit-box-orient: vertical;
   overflow: hidden;
```
labels: ["tasks", "tech-debt", "ui", "react", "fastapi", "refactor"]
links:
  spec: "specs/002-tech-debt-ui-fixes/spec.md"
  plan: "specs/002-tech-debt-ui-fixes/plan.md"
  tasks: "specs/002-tech-debt-ui-fixes/tasks.md"
  ticket: null
  adr: null
  pr: null
files: []
tests: []
---

# Prompt History Record

## PROMPT_TEXT

/sp.tasks

1. **Backend Audit:** Verify the FastAPI `main.py` file. Locate the translation POST route. If it's missing or named incorrectly, fix it to match the frontend call in `UrduTranslator.tsx`.
2. **Frontend React Fix:** Open `src/components/personalize/PersonalizeButton.jsx`. Remove `jsx={true}` or `jsx` from any HTML tags. If using styled-jsx, ensure it is configured correctly in docusaurus.config.js.
3. **DOM Lifecycle Fix:** Refactor `src/components/translate-widget.js`. Instead of running raw script logic, wrap the button detection in a `window.addEventListener('load')` or move the logic into the `UrduTranslator` component's `useEffect`.
4. **CSS Standardization:** Edit `styles.css`. Replace `line-clamp: 14` with:
   ```css
   display: -webkit-box;
   -webkit-line-clamp: 14;
   -webkit-box-orient: vertical;
   overflow: hidden;
```

## RESPONSE_TEXT

Successfully created comprehensive task breakdown for the technical debt and UI bug fixes. The tasks.md file includes:

1. Seven implementation phases:
   - Phase 1: Setup (initial configuration)
   - Phase 2: Foundational (discovery and analysis)
   - Phase 3: PersonalizeButton fix (US1 - P1 priority)
   - Phase 4: Urdu Translation API fix (US2 - P1 priority)
   - Phase 5: Urdu Widget DOM access fix (US3 - P2 priority)
   - Phase 6: CSS standardization (US4 - P2 priority)
   - Phase 7: Integration and testing

2. 36 specific tasks with proper formatting:
   - Each task follows the required format: - [ ] T### [P?] [US?] Description with file path
   - Parallel tasks marked with [P] flag
   - User story tasks marked with [US] labels
   - Clear file paths and actionable descriptions

3. Dependencies and parallel execution opportunities identified
4. Implementation strategy with MVP approach defined

The tasks address all user requirements including backend audit, PersonalizeButton jsx prop fix, DOM lifecycle refactoring, and CSS standardization.

## OUTCOME

Task breakdown created successfully in specs/002-tech-debt-ui-fixes/tasks.md with corresponding checklist in specs/002-tech-debt-ui-fixes/checklists/tasks.md. Ready for implementation phase.