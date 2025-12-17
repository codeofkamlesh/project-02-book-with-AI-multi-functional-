# API Contract: RAG Chatbot for Physical AI & Humanoid Robotics Textbook

## Overview
This document defines the API contract for the RAG (Retrieval-Augmented Generation) chatbot that provides answers based on textbook content.

## Base URL
`http://localhost:8000/api/v1` (development)
`https://[your-domain]/api/v1` (production)

## Authentication
All endpoints require authentication via API key in the header:
```
Authorization: Bearer {api_key}
```

## Endpoints

### POST /query
Submit a query to the RAG system and receive an AI-generated response based on textbook content.

#### Request
```json
{
  "query": "string, the user's question",
  "selected_text": "string, optional highlighted text for context",
  "session_id": "string, optional session identifier",
  "user_context": {
    "background": "string, user's technical background",
    "preferences": "object, user preferences for response style"
  }
}
```

#### Response
```json
{
  "response": "string, the AI-generated answer",
  "sources": [
    {
      "doc_path": "string, path to source document",
      "heading": "string, relevant heading from source",
      "section": "string, section identifier",
      "relevance_score": "number, 0-1 similarity score"
    }
  ],
  "session_id": "string, session identifier (new or existing)",
  "provenance": "string, information about how the response was generated"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid authentication
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Processing error

### POST /ingest/docs
Ingest textbook content into the RAG system.

#### Request
```json
{
  "documents": [
    {
      "doc_path": "string, unique identifier for the document",
      "content": "string, full text content of the document",
      "metadata": {
        "title": "string, document title",
        "section": "string, textbook section",
        "heading": "string, main heading",
        "last_modified": "string, ISO date string"
      }
    }
  ]
}
```

#### Response
```json
{
  "status": "string, success or error",
  "processed_docs": "number, count of documents processed",
  "chunks_created": "number, count of content chunks created",
  "details": [
    {
      "doc_path": "string, document identifier",
      "status": "string, success or error",
      "chunks": "number, chunks created for this document"
    }
  ]
}
```

### GET /session/{session_id}
Retrieve conversation history for a specific session.

#### Response
```json
{
  "session_id": "string",
  "created_at": "string, ISO date",
  "last_active": "string, ISO date",
  "messages": [
    {
      "id": "string",
      "role": "string, user|assistant",
      "content": "string",
      "timestamp": "string, ISO date",
      "sources": ["string, document paths"]
    }
  ]
}
```

### DELETE /session/{session_id}
Delete a conversation session and its history.

#### Response
```json
{
  "status": "string, deleted",
  "session_id": "string"
}
```

### POST /query/feedback
Submit feedback on a response to improve the system.

#### Request
```json
{
  "query_id": "string, identifier for the original query",
  "response_id": "string, identifier for the response",
  "rating": "number, 1-5 star rating",
  "comment": "string, optional feedback comment",
  "is_accurate": "boolean, whether the response was accurate",
  "is_helpful": "boolean, whether the response was helpful"
}
```

#### Response
```json
{
  "status": "string, submitted",
  "feedback_id": "string, unique identifier for the feedback"
}
```

## Data Types

### Query Object
- `query`: Required string, 1-1000 characters
- `selected_text`: Optional string, 1-5000 characters
- `session_id`: Optional string, 1-100 characters
- `user_context`: Optional object with background and preferences

### Response Object
- `response`: Required string, the AI-generated answer
- `sources`: Required array of source objects with provenance
- `session_id`: Required string, session identifier
- `provenance`: Required string, generation information

## Rate Limits
- Query endpoint: 100 requests per minute per API key
- Ingest endpoint: 10 requests per minute per API key

## Error Format
All error responses follow this format:
```json
{
  "error": {
    "code": "string, error code",
    "message": "string, human-readable error message",
    "details": "object, optional additional error details"
  }
}
```

## Versioning
This API follows semantic versioning. The current version is v1, indicated in the URL path.