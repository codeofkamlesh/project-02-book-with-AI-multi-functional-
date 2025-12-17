"""
Text chunking module for the Physical AI & Humanoid Robotics RAG system.
Implements sentence-aware chunking with overlap preservation and code block detection.
"""
import re
from typing import List, Dict, Any
import hashlib
from typing import Optional

class DocumentChunker:
    """
    Implements intelligent document chunking for RAG system
    """

    def __init__(self, chunk_size: int = 900, overlap_size: int = 150, separator: str = "\n\n"):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.separator = separator

    def chunk_document(self, text: str, path: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks while preserving semantic boundaries
        """
        # Remove frontmatter if present
        text = self._remove_frontmatter(text)

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        chunk_id_counter = 0

        for para_idx, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) == 0:
                continue

            # If paragraph is too large, split it further
            sub_chunks = self._split_large_paragraph(paragraph)

            for sub_chunk in sub_chunks:
                chunk_text = sub_chunk.strip()
                if len(chunk_text) == 0:
                    continue

                # Create chunk with metadata
                chunk = {
                    "chunk_id": f"{hashlib.sha1((path + str(para_idx) + str(chunk_id_counter)).encode()).hexdigest()[:16]}",
                    "doc_id": hashlib.sha1(path.encode()).hexdigest()[:16],
                    "title": title,
                    "path": path,
                    "source_text": chunk_text,
                    "is_code_block": self._contains_code_block(chunk_text),
                    "char_count": len(chunk_text),
                    "token_estimate": len(chunk_text.split())  # Rough token estimation
                }

                chunks.append(chunk)
                chunk_id_counter += 1

        # Apply sliding window to create overlaps
        chunks_with_overlap = self._apply_sliding_window(chunks)

        return chunks_with_overlap

    def _remove_frontmatter(self, text: str) -> str:
        """Remove YAML frontmatter if present"""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return parts[2]  # Return content after frontmatter
        return text

    def _split_large_paragraph(self, text: str) -> List[str]:
        """Split large paragraphs into smaller chunks"""
        if self._estimate_tokens(text) <= self.chunk_size:
            return [text]

        # Try to split by sentences
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if self._estimate_tokens(current_chunk + " " + sentence) <= self.chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # If still too large, split by words
        if chunks and self._estimate_tokens(chunks[-1]) > self.chunk_size:
            final_chunks = []
            for chunk in chunks:
                if self._estimate_tokens(chunk) > self.chunk_size:
                    final_chunks.extend(self._split_by_words(chunk))
                else:
                    final_chunks.append(chunk)
            return final_chunks

        return chunks

    def _split_by_words(self, text: str) -> List[str]:
        """Split text by words when sentence splitting isn't sufficient"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _apply_sliding_window(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply sliding window with overlap between chunks"""
        if len(chunks) <= 1:
            return chunks

        result = []

        for i, chunk in enumerate(chunks):
            # Add current chunk
            result.append(chunk.copy())

            # Add overlap with next chunk if it exists
            if i < len(chunks) - 1:
                # Create overlapping chunk with some content from current and next
                next_chunk = chunks[i + 1]

                # Extract overlapping content from end of current chunk
                current_words = chunk["source_text"].split()
                overlap_from_current = current_words[-self.overlap_size:]

                if overlap_from_current:
                    overlap_text = " ".join(overlap_from_current)
                    overlap_chunk = {
                        "chunk_id": f"{chunk['chunk_id']}_overlap_{i}",
                        "doc_id": chunk["doc_id"],
                        "title": chunk["title"],
                        "path": chunk["path"],
                        "source_text": overlap_text,
                        "is_code_block": self._contains_code_block(overlap_text),
                        "char_count": len(overlap_text),
                        "token_estimate": len(overlap_text.split())
                    }
                    result.append(overlap_chunk)

        return result

    def _contains_code_block(self, text: str) -> bool:
        """Detect if text contains code blocks"""
        return "```" in text or "`" in text or any(keyword in text.lower() for keyword in
                ["def ", "class ", "import ", "from ", "var ", "function ", "int ", "float ", "bool "])

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token = 4 chars or 1 word)"""
        return max(len(text) // 4, len(text.split()))


# Example usage
if __name__ == "__main__":
    chunker = DocumentChunker()
    sample_text = """---
sidebar_position: 1
---

# Introduction to Physical AI & Humanoid Robotics

Welcome to the comprehensive guide to humanoid robotics using modern tools and frameworks. This book covers the complete pipeline from basic ROS 2 concepts to advanced Vision-Language-Action (VLA) systems for humanoid robot control.

## Book Structure

This book follows a 4-model architecture:

1. **ROS2 Foundations** - Core concepts of Robot Operating System 2
2. **Simulation** - Gazebo and Unity environments for robot simulation
3. **NVIDIA Isaac** - Isaac Sim and Isaac ROS for perception and control
4. **Vision-Language-Action (VLA)** - Multimodal AI for humanoid control

Each section builds upon the previous one, providing a comprehensive learning path from basic concepts to advanced applications.
"""

    chunks = chunker.chunk_document(sample_text, "/docs/intro.md", "Introduction")
    print(f"Generated {len(chunks)} chunks from sample document")
    for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
        print(f"\nChunk {i+1}: {chunk['chunk_id']}")
        print(f"Size: {len(chunk['source_text'])} chars, ~{chunk['token_estimate']} tokens")
        print(f"Is code: {chunk['is_code_block']}")
        print(f"Content preview: {chunk['source_text'][:100]}...")