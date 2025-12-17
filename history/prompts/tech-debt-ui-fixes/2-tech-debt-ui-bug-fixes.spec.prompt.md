---
id: 2
title: "Technical Debt & UI Bug Fixes Spec"
stage: spec
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: tech-debt-ui-fixes
branch: 002-tech-debt-ui-fixes
user: user
command: "/sp.specify Technical Debt & UI Bug Fixes for Robotics Textbook

Goal: Resolve critical frontend errors and API 404s in the Urdu Translation and Personalization features.

Success criteria:
- Eliminate React hydration warning "non-boolean attribute jsx" in PersonalizeButton.
- Fix Urdu translation "Not Found" error by correcting the API route in the backend.
- Ensure the Urdu widget correctly finds the DOM element using React refs or Docusaurus lifecycle hooks instead of direct DOM manipulation.
- Standardize CSS to remove "Unknown property" warnings.

Constraints:
- No "vibe coding": Do not delete features to hide errors; fix the root logic.
- Backend fixes must align with FastAPI route definitions.
- Maintain Docusaurus Best Practices for component mounting."
labels: ["ui", "debugging", "tech-debt", "react", "css", "api", "fixes"]
links:
  spec: "specs/002-tech-debt-ui-fixes/spec.md"
  tasks: null
  ticket: null
  adr: null
  pr: null
files: []
tests: []
---

# Prompt History Record

## PROMPT_TEXT

Technical Debt & UI Bug Fixes for Robotics Textbook

Goal: Resolve critical frontend errors and API 404s in the Urdu Translation and Personalization features.

Success criteria:
- Eliminate React hydration warning "non-boolean attribute jsx" in PersonalizeButton.
- Fix Urdu translation "Not Found" error by correcting the API route in the backend.
- Ensure the Urdu widget correctly finds the DOM element using React refs or Docusaurus lifecycle hooks instead of direct DOM manipulation.
- Standardize CSS to remove "Unknown property" warnings.

Constraints:
- No "vibe coding": Do not delete features to hide errors; fix the root logic.
- Backend fixes must align with FastAPI route definitions.
- Maintain Docusaurus Best Practices for component mounting.

## RESPONSE_TEXT

Successfully created feature specification for technical debt and UI bug fixes in the Robotics Textbook application. The specification addresses four main issues:

1. React hydration warnings in PersonalizeButton component
2. Urdu translation API 404 errors
3. DOM element access issues in Urdu widget
4. CSS validation warnings

The spec includes:
- User stories with priorities (P1-P2)
- Functional requirements (FR-TECH-001 to FR-TECH-007)
- Key entities identification
- Measurable success criteria (SC-TECH-001 to SC-TECH-008)
- A quality checklist confirming all validation items completed

The specification ensures existing functionality is maintained while fixing the technical debt and UI bugs as requested, following the constraints of no "vibe coding" and maintaining Docusaurus best practices.

## OUTCOME

Feature specification created successfully in specs/002-tech-debt-ui-fixes/spec.md with corresponding checklist in specs/002-tech-debt-ui-fixes/checklists/requirements.md. Ready for planning phase.