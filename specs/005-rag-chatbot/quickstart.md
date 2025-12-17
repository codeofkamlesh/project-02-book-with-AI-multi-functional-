# Quickstart: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Textbook

## Prerequisites

- Python 3.8+ for backend services
- Node.js 16+ for Docusaurus frontend
- OpenAI API key for embeddings and chat completion
- Qdrant Cloud account for vector storage
- Neon Postgres account for metadata storage

## Setup

### 1. Backend Setup

1. Navigate to the rag_backend directory:
   ```bash
   cd rag_backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   NEON_DATABASE_URL=your_neon_postgres_connection_string
   ```

4. Start the FastAPI server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

### 2. Vector Database Setup

1. Initialize the Qdrant collection for document chunks:
   ```python
   # Run the ingestion script to create the collection and index
   python -m rag_backend.pipeline.ingest
   ```

2. The script will:
   - Create a collection named "textbook_chunks"
   - Set up the vector index with 1536 dimensions (for text-embedding-3-small)
   - Configure metadata fields for filtering

### 3. Frontend Integration

1. Navigate to the docusaurus directory:
   ```bash
   cd docusaurus
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the chat widget:
   ```bash
   npm run build
   ```

4. Start the development server:
   ```bash
   npm start
   ```

### 4. API Endpoints

- Query endpoint: `POST /api/v1/query`
  - Request: `{ "query": "your question", "selected_text": "optional selected text", "session_id": "optional session id" }`
  - Response: `{ "response": "answer", "sources": ["document paths"], "session_id": "session id" }`

- Ingestion endpoint: `POST /api/v1/ingest`
  - Request: `{ "doc_path": "path/to/document", "content": "document content" }`
  - Response: `{ "status": "success", "chunks_created": 5 }`

## Usage

### Basic Query
Send a query to get answers from the textbook content:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain ROS2 architecture"}'
```

### Selected Text Mode
Query with selected text context:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What does this mean?", "selected_text": "The ROS2 architecture consists of..."}'
```

### Frontend Integration
The chat widget will be automatically integrated into the Docusaurus layout and accessible from any textbook page.

## Testing

1. Unit tests for backend:
   ```bash
   cd rag_backend
   pytest tests/unit/
   ```

2. Integration tests:
   ```bash
   cd rag_backend
   pytest tests/integration/
   ```

3. Frontend tests:
   ```bash
   cd docusaurus
   npm test
   ```

## Troubleshooting

- If the chat widget doesn't appear, verify that the RAG plugin is properly loaded in docusaurus.config.js
- If queries return no results, check that documents have been properly ingested into Qdrant
- If API calls fail, verify that environment variables are properly set