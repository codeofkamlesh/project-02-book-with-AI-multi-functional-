# Research: Integrated RAG Chatbot for Physical AI & Humanoid Robotics Textbook

## Decision: Embedding Model Choice
**Rationale**: Selected OpenAI text-embedding-3-small for its balance of performance and cost-effectiveness for technical documentation. This model provides 1536 dimensions which is sufficient for capturing semantic meaning in robotics and AI concepts while being more cost-effective than larger models.

**Alternatives considered**:
- text-embedding-ada-002: Higher dimensional (1536) but older model, good performance
- sentence-transformers/all-MiniLM-L6-v2: Open source alternative, lower dimensional (384) but free to use
- Cohere embed-english-light: Alternative commercial option with good technical content support

## Decision: Chunking Strategy for Technical Documentation
**Rationale**: Implemented hierarchical chunking that preserves code snippets and maintains context. The strategy uses:
- Document-level chunks for complete sections
- Paragraph-level chunks for detailed content
- Code-block preservation to maintain technical accuracy
- Overlapping windows to maintain context across chunks

This ensures that code snippets remain intact and technical explanations maintain their context while enabling effective retrieval.

**Alternatives considered**:
- Fixed-size token chunks: Could split code blocks and break technical explanations
- Sentence-level chunks: Too granular for technical content, loses context
- Semantic chunking: More sophisticated but potentially inconsistent for technical documentation

## Decision: Selected Text Integration Method
**Rationale**: Using window.getSelection() API for browser-based text selection with additional context preservation. This method:
- Works across all modern browsers
- Preserves formatting and context of selected text
- Integrates seamlessly with Docusaurus content structure
- Allows for additional metadata extraction (heading context, document location)

**Alternatives considered**:
- Custom selection handlers: More complex to implement, browser compatibility issues
- Mutation observers: Overly complex for simple text selection
- Docusaurus-specific plugins: Limited flexibility and potential conflicts with existing plugins

## Decision: Vector Database Schema in Qdrant
**Rationale**: Designed schema with metadata fields to support filtering and contextual retrieval:
- payload: {content, doc_path, heading, section, embedding_metadata}
- Vector storage optimized for semantic search in technical content
- Metadata fields to support filtering and provenance tracking

**Alternatives considered**:
- Simple content-only vectors: Would lack provenance and filtering capabilities
- Multiple collections per document type: Would complicate retrieval logic
- Alternative vector databases (Pinecone, Weaviate): Qdrant chosen for compatibility with existing stack

## Decision: Frontend Integration Approach
**Rationale**: Using React-based ChatKit component that integrates with Docusaurus theme system:
- Non-disruptive overlay that preserves existing layout
- Consistent with existing Docusaurus component patterns
- Responsive design that works across device sizes
- Proper state management for conversation history

**Alternatives considered**:
- Iframe embedding: Would create styling and communication challenges
- Complete UI rewrite: Too disruptive to existing user experience
- Standalone application: Would lose textbook context and navigation