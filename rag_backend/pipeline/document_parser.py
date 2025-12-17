"""
Document parser for the RAG Chatbot system.
Handles parsing of textbook content from various formats (markdown, etc.) into structured chunks.
"""
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import markdown
from bs4 import BeautifulSoup


class DocumentParser:
    """
    Parser for textbook content that handles various formats and creates structured chunks
    with proper heading and section context.
    """

    def __init__(self):
        self.supported_formats = ['.md', '.txt', '.html', '.htm']

    def parse_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a document and return a list of content chunks with metadata

        Args:
            file_path: Path to the document to parse

        Returns:
            List of document chunks with content, heading, section, and metadata
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {extension}. Supported: {self.supported_formats}")

        content = self._read_file(file_path)

        if extension in ['.md', '.txt']:
            return self._parse_markdown(content, file_path)
        elif extension in ['.html', '.htm']:
            return self._parse_html(content, file_path)
        else:
            # Default to plain text parsing
            return self._parse_plain_text(content, file_path)

    def _read_file(self, file_path: str) -> str:
        """
        Read file content with proper encoding handling
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    def _parse_markdown(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse markdown content into structured chunks
        """
        chunks = []

        # Split content by headings to preserve context
        lines = content.split('\n')
        current_heading = None
        current_section = None
        current_content = []

        for line in lines:
            # Check for markdown headings (h1, h2, h3)
            heading_match = re.match(r'^(#{1,3})\s+(.+)', line)
            if heading_match:
                # If we have accumulated content, save it as a chunk
                if current_content and any(part.strip() for part in current_content):
                    chunk_content = '\n'.join(current_content).strip()
                    if chunk_content:
                        chunks.append({
                            'content': chunk_content,
                            'doc_path': file_path,
                            'heading': current_heading,
                            'section': current_section,
                            'metadata': {
                                'file_type': 'markdown',
                                'source_line_count': len(chunk_content.split('\n'))
                            }
                        })

                # Update current heading based on heading level
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                if heading_level == 1:
                    current_section = heading_text
                    current_heading = None  # Reset sub-heading
                elif heading_level == 2:
                    current_heading = heading_text
                elif heading_level == 3:
                    # For h3, combine with h2 if available
                    current_heading = f"{current_heading or ''} - {heading_text}".strip(' - ')

                # Start new content collection
                current_content = [line]
            else:
                current_content.append(line)

        # Don't forget the last chunk
        if current_content and any(part.strip() for part in current_content):
            chunk_content = '\n'.join(current_content).strip()
            if chunk_content:
                chunks.append({
                    'content': chunk_content,
                    'doc_path': file_path,
                    'heading': current_heading,
                    'section': current_section,
                    'metadata': {
                        'file_type': 'markdown',
                        'source_line_count': len(chunk_content.split('\n'))
                    }
                })

        return self._chunk_large_sections(chunks)

    def _parse_html(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content into structured chunks
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extract text while preserving structure
        chunks = []
        current_heading = None
        current_section = None

        # Find all headings and content between them
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section', 'article'])

        for element in elements:
            tag = element.name
            text = element.get_text().strip()

            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Save previous content as chunk if exists
                if text:
                    if tag == 'h1':
                        current_section = text
                        current_heading = None
                    elif tag == 'h2':
                        current_heading = text
                    elif tag == 'h3':
                        current_heading = f"{current_heading or ''} - {text}".strip(' - ')

            elif text and tag in ['p', 'div', 'section', 'article']:
                # Add content chunk with current context
                if text and len(text) > 20:  # Only add meaningful content
                    chunks.append({
                        'content': text,
                        'doc_path': file_path,
                        'heading': current_heading,
                        'section': current_section,
                        'metadata': {
                            'file_type': 'html',
                            'html_tag': tag
                        }
                    })

        return self._chunk_large_sections(chunks)

    def _parse_plain_text(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse plain text content into chunks
        """
        chunks = []

        # Split by paragraphs (double newlines)
        paragraphs = content.split('\n\n')

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and len(paragraph) > 20:  # Only add meaningful content
                chunks.append({
                    'content': paragraph,
                    'doc_path': file_path,
                    'heading': None,
                    'section': None,
                    'metadata': {
                        'file_type': 'text',
                        'source_line_count': len(paragraph.split('\n'))
                    }
                })

        return self._chunk_large_sections(chunks)

    def _chunk_large_sections(self, chunks: List[Dict[str, Any]], max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Split large chunks into smaller ones while preserving context

        Args:
            chunks: List of document chunks to potentially split
            max_chunk_size: Maximum size of a chunk in characters

        Returns:
            List of potentially split document chunks
        """
        result_chunks = []

        for chunk in chunks:
            content = chunk['content']

            if len(content) <= max_chunk_size:
                result_chunks.append(chunk)
            else:
                # Split large content into smaller chunks
                sentences = re.split(r'[.!?]+', content)
                current_chunk_parts = []
                current_size = 0

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if current_size + len(sentence) <= max_chunk_size:
                        current_chunk_parts.append(sentence)
                        current_size += len(sentence)
                    else:
                        # Save current chunk and start a new one
                        if current_chunk_parts:
                            result_chunks.append({
                                **chunk,  # Copy all original properties
                                'content': '. '.join(current_chunk_parts) + '.',
                                'metadata': {
                                    **chunk['metadata'],
                                    'chunk_index': len(result_chunks),
                                    'is_split_chunk': True
                                }
                            })

                        # Start new chunk with current sentence
                        current_chunk_parts = [sentence]
                        current_size = len(sentence)

                # Add remaining sentences as a chunk
                if current_chunk_parts:
                    result_chunks.append({
                        **chunk,  # Copy all original properties
                        'content': '. '.join(current_chunk_parts) + '.',
                        'metadata': {
                            **chunk['metadata'],
                            'chunk_index': len(result_chunks),
                            'is_split_chunk': True
                        }
                    })

        return result_chunks

    def parse_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Parse all supported documents in a directory

        Args:
            directory_path: Path to the directory to parse
            recursive: Whether to recursively parse subdirectories

        Returns:
            List of document chunks from all files in the directory
        """
        all_chunks = []
        directory = Path(directory_path)

        if recursive:
            pattern = '**/*.*'
        else:
            pattern = '*.*'

        for file_path in directory.glob(pattern):
            if file_path.suffix.lower() in self.supported_formats:
                try:
                    file_chunks = self.parse_document(str(file_path))
                    all_chunks.extend(file_chunks)
                except Exception as e:
                    print(f"Error parsing {file_path}: {str(e)}")

        return all_chunks


# Global instance
document_parser = DocumentParser()


def parse_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Convenience function to parse a document
    """
    return document_parser.parse_document(file_path)


def parse_directory(directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """
    Convenience function to parse all documents in a directory
    """
    return document_parser.parse_directory(directory_path, recursive)