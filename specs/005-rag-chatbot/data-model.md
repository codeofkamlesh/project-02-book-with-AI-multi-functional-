# Data Model: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Textbook

## Entities

### ChatSession
Represents a user's interaction session with the chatbot

**Fields**:
- id: string (unique identifier)
- userId: string (optional, for logged-in users)
- createdAt: timestamp
- lastActiveAt: timestamp
- messages: array of Message objects
- metadata: object (additional session data)

**Relationships**:
- Contains many Message entities
- Optionally linked to User (if authenticated)

### Message
Represents a single message in a conversation

**Fields**:
- id: string (unique identifier)
- sessionId: string (foreign key to ChatSession)
- role: string (user|assistant)
- content: string (message text)
- timestamp: timestamp
- context: object (retrieval context for the message)
- sources: array of strings (document sources used for response)

**Relationships**:
- Belongs to one ChatSession
- References document chunks in vector database

### DocumentChunk
Represents a chunk of textbook content in the vector database

**Fields**:
- id: string (unique identifier for vector database)
- content: string (the text content)
- docPath: string (path to source document)
- heading: string (associated heading context)
- section: string (section identifier)
- embedding: vector (the embedding vector)
- metadata: object (additional chunk metadata)

**Relationships**:
- Referenced by multiple Message entities as sources

### UserQuery
Represents a user's query and associated metadata

**Fields**:
- id: string (unique identifier)
- sessionId: string (foreign key to ChatSession)
- queryText: string (original user query)
- selectedText: string (highlighted text context, optional)
- processedAt: timestamp
- retrievalResults: array of DocumentChunk references
- responseGenerated: boolean

**Relationships**:
- Belongs to one ChatSession
- References multiple DocumentChunk entities

### RetrievalResult
Represents the results of a vector search operation

**Fields**:
- id: string (unique identifier)
- queryId: string (foreign key to UserQuery)
- chunkId: string (reference to DocumentChunk)
- similarityScore: float (cosine similarity score)
- rank: integer (rank in results)
- metadata: object (additional retrieval metadata)

**Relationships**:
- Belongs to one UserQuery
- References one DocumentChunk

## State Transitions

### ChatSession
- Created → Active → Inactive
  - Created when user first opens chat
  - Active while user is interacting
  - Inactive after timeout or explicit close

### Message
- Pending → Processed → Completed
  - Pending while waiting for response
  - Processed during RAG pipeline execution
  - Completed when response is returned to user

## Validation Rules

1. **ChatSession**:
   - Must have valid timestamp for createdAt
   - Session must expire after 30 minutes of inactivity

2. **Message**:
   - Content must not exceed 10,000 characters
   - Role must be either "user" or "assistant"

3. **DocumentChunk**:
   - Content must be between 50 and 2000 tokens
   - Must have valid docPath reference

4. **UserQuery**:
   - Must have non-empty queryText or selectedText
   - Cannot have more than 10 retrieval results per query

## Indexes

1. ChatSession: userId (if present), createdAt
2. Message: sessionId, timestamp
3. DocumentChunk: docPath, heading (for filtering)
4. UserQuery: sessionId, processedAt