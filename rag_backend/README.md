# Physical AI & Humanoid Robotics RAG Backend

This is the backend service for the Physical AI & Humanoid Robotics book project, providing RAG (Retrieval-Augmented Generation) capabilities, authentication, personalization, and translation services.

## Features

- **RAG Chatbot**: Intelligent question-answering system that uses book content
- **Highlight-to-Ask**: Ask questions about selected text
- **Persistent Chat**: Chat sessions that persist across pages
- **Personalization**: Content adaptation based on user profile
- **Urdu Translation**: Toggle between English and Urdu
- **Authentication**: Better-Auth integration with profile questions
- **Reusable Intelligence**: Subagent system for AI-powered tasks

## Architecture

The backend is built with:
- **FastAPI**: Web framework for API endpoints
- **Qdrant**: Vector database for document retrieval
- **Neon Postgres**: Database for user profiles and caching
- **OpenAI API**: For RAG, personalization, and translation
- **Python**: Primary implementation language

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database (Neon)
- Qdrant Cloud account
- OpenAI API key
- Better-Auth (for frontend integration)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd project-01-book-with-AI
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
NEON_DATABASE_URL=your_neon_database_url
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
RAG_API_SECRET=your_api_secret
BETTER_AUTH_CLIENT_ID=your_better_auth_client_id
BETTER_AUTH_CLIENT_SECRET=your_better_auth_client_secret
```

## Database Setup

1. Create the database schema by running the SQL in `db/neon_schema.sql`:
   ```sql
   -- Execute neon_schema.sql in your Neon database
   ```

## Qdrant Setup

1. Create a Qdrant collection using the schema in `qdrant/schema.yaml`
2. The application will automatically initialize the collection if it doesn't exist

## Running the Application

### Development

```bash
cd rag-backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
cd rag-backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### RAG Query
- `POST /api/v1/query` - Query the RAG system
- `POST /api/v1/session/answer-context` - Save conversation context

### Document Ingestion
- `POST /api/v1/ingest/docs` - Ingest documents into the system
- `POST /api/v1/reindex` - Reindex all documents

### Authentication
- `POST /api/v1/auth/better-auth-callback` - Better-Auth integration
- `POST /api/v1/auth/profile` - Save user profile
- `GET /api/v1/auth/me` - Get current user info

### Personalization
- `POST /api/v1/personalize/render` - Personalize content

### Translation
- `POST /api/v1/translate/urdu` - Translate to Urdu

### Health Check
- `GET /api/v1/status` - Health check endpoint
- `GET /` - Root endpoint

## Frontend Integration

The backend is designed to work with the Docusaurus frontend in the `docusaurus/` directory. The RAG chat widget, personalization, and translation features are integrated into the book pages.

## Subagents

The system includes a subagent framework for reusable intelligence:

- **ROS2 Code Generator**: Generates ROS2 code snippets and node skeletons
- **Gazebo Scene Creator**: Creates Gazebo world files and SDF models
- **Quiz Generator**: Creates quizzes based on book content

## Testing

Run the tests:

```bash
cd rag-backend
python -m pytest tests/ -v
```

## Deployment

### Docker (Optional)

A Dockerfile can be created for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The service can be deployed to:
- AWS (using EC2, ECS, or Lambda)
- Google Cloud Platform (using Cloud Run or Compute Engine)
- Azure (using App Service or Container Instances)
- Vercel, Netlify (for serverless functions)

## Security

- API endpoints are secured with appropriate authentication
- Rate limiting is implemented to prevent abuse
- User data is stored securely in Neon Postgres
- Environment variables keep secrets out of code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Specify your license here]

## Support

For support, please open an issue in the GitHub repository.