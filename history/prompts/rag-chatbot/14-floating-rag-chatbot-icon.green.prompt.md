---
id: 14
title: "Floating RAG Chatbot Icon on Book Pages"
stage: green
date: "2025-12-17"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "rag-chatbot"
branch: "main"
user: "user"
command: "/sp.implement make a floating icon for RAG chabot in the right bottom cornor of the book  page not on the Home page."
labels: ["ui", "chatbot", "rag", "floating-widget"]
spec: null
ticket: null
adr: null
pr: null
---

## Summary

### PROMPT_TEXT
```
make a floating icon for RAG chabot in the right bottom cornor of the book  page not on the Home page.
```

### RESPONSE_TEXT

Successfully implemented a floating RAG chatbot icon that appears in the bottom right corner of book pages but not on the home page. Here's what was done:

1. **Enabled existing ChatWidget**: The ChatWidget component already existed in the codebase and was positioned correctly in the bottom right corner, but was temporarily disabled in the Root.jsx file. I enabled it by uncommenting the component.

2. **Added conditional rendering**: Modified the ChatWidget component to use the Docusaurus router's useLocation hook to detect the current page path and only render on book pages (paths starting with '/docs/').

3. **Preserved existing functionality**: The ChatWidget already had proper CSS positioning (position: fixed, bottom: 20px, right: 20px) to place it in the bottom right corner.

### FILES_TOUCHED
- docusaurus\src\components\rag\ChatWidget.jsx
- docusaurus\src\theme\Root.jsx

### OUTCOME
The RAG chatbot floating icon now appears in the bottom right corner of book pages (documentation pages) but is hidden on the home page and other non-book pages.

### EVALUATION
The implementation successfully meets the requirements: a floating chatbot icon appears in the bottom right corner of book pages only, not on the home page. The existing functionality of the chatbot is preserved while adding the conditional display logic.