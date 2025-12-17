"""
RAG Agent for the Physical AI & Humanoid Robotics RAG system.
Handles the generation of responses based on retrieved context using OpenAI models.
"""
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from ..pipeline.rag import process_query


class RAGAgent:
    """
    Agent that handles response generation using retrieved context from RAG pipeline
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_response(self, query: str, context_chunks: List[Dict[str, Any]],
                               user_profile: Optional[Dict[str, Any]] = None,
                               selected_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response based on the query and retrieved context

        Args:
            query: User's original query
            context_chunks: List of retrieved context chunks from RAG pipeline
            user_profile: Optional user profile for personalization
            selected_text: Optional selected/highlighted text from the user

        Returns:
            Dictionary containing the generated response and metadata
        """
        try:
            # Prepare context from retrieved chunks
            context_texts = [chunk['content'] for chunk in context_chunks]
            context_str = "\n\n".join(context_texts)

            # Build the prompt for the LLM
            prompt = self._build_prompt(query, context_str, user_profile, selected_text)

            # Generate response using OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(user_profile)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000,
                top_p=0.9
            )

            # Extract the generated response
            generated_text = response.choices[0].message.content

            # Prepare sources information
            sources = []
            for chunk in context_chunks:
                source_info = {
                    'doc_path': chunk['doc_path'],
                    'heading': chunk['heading'],
                    'section': chunk['section'],
                    'similarity_score': chunk['similarity_score']
                }
                sources.append(source_info)

            # Prepare the response
            result = {
                'query': query,
                'response': generated_text,
                'sources': sources,
                'context_used': context_str[:1000] + "..." if len(context_str) > 1000 else context_str,
                'model_used': self.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': response.usage.total_tokens if response.usage else 0
                }
            }

            return result

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'query': query,
                'response': f"Sorry, I encountered an error processing your request: {str(e)}",
                'sources': [],
                'context_used': '',
                'error': str(e)
            }

    def _build_prompt(self, query: str, context: str, user_profile: Optional[Dict[str, Any]] = None,
                     selected_text: Optional[str] = None) -> str:
        """
        Build the prompt for the LLM based on query, context, and user profile
        """
        prompt_parts = []

        # Add selected text context if provided
        if selected_text:
            prompt_parts.append(f"The user has selected/highlighted this text: '{selected_text}'")
            prompt_parts.append(f"The user's question about this selected text is: '{query}'")
        else:
            prompt_parts.append(f"The user's question is: '{query}'")

        # Add context from RAG
        prompt_parts.append("\nBased on the following textbook content, please answer the user's question:")
        prompt_parts.append(f"\n{context}")

        # Add user profile information if available
        if user_profile:
            profile_parts = []
            if user_profile.get('software_background'):
                profile_parts.append(f"User's software background: {user_profile['software_background']}")
            if user_profile.get('hardware_background'):
                profile_parts.append(f"User's hardware background: {user_profile['hardware_background']}")
            if user_profile.get('preferences'):
                profile_parts.append(f"User's preferences: {user_profile['preferences']}")

            if profile_parts:
                prompt_parts.append(f"\nUser profile information: {'; '.join(profile_parts)}")
                prompt_parts.append("Please tailor your response to match the user's background and preferences.")

        return "\n".join(prompt_parts)

    def _get_system_prompt(self, user_profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Get the system prompt for the LLM
        """
        base_prompt = (
            "You are an expert AI assistant for the Physical AI & Humanoid Robotics textbook. "
            "Your role is to provide accurate, helpful answers based on the textbook content provided in the context. "
            "Always cite specific information from the context when answering. "
            "If the context doesn't contain information to answer the question, clearly state that the information is not available in the provided materials."
        )

        # Add personalization based on user profile
        if user_profile:
            profile_notes = []
            software_bg = user_profile.get('software_background', {})
            hardware_bg = user_profile.get('hardware_background', {})

            if software_bg.get('level') == 'beginner':
                profile_notes.append("The user is a beginner in software development. Provide detailed explanations and avoid overly technical jargon.")
            elif software_bg.get('level') == 'advanced':
                profile_notes.append("The user is an advanced developer. You can use technical terminology and provide in-depth explanations.")

            if hardware_bg.get('experience') and 'beginner' in hardware_bg.get('experience', '').lower():
                profile_notes.append("The user is new to hardware concepts. Explain hardware-related concepts clearly.")
            elif hardware_bg.get('experience') and 'advanced' in hardware_bg.get('experience', '').lower():
                profile_notes.append("The user has advanced hardware experience. You can discuss complex hardware topics.")

            if profile_notes:
                base_prompt += " " + " ".join(profile_notes)

        return base_prompt

    async def query_with_rag(self, query: str, doc_path_filter: Optional[str] = None,
                            user_profile: Optional[Dict[str, Any]] = None,
                            selected_text: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Complete RAG query: retrieve context and generate response

        Args:
            query: User's query
            doc_path_filter: Optional filter to limit search to specific document
            user_profile: Optional user profile for personalization
            selected_text: Optional selected/highlighted text from the user
            limit: Maximum number of chunks to retrieve

        Returns:
            Dictionary containing the generated response and metadata
        """
        # First, retrieve relevant context using RAG pipeline
        rag_result = await process_query(query, doc_path_filter, limit)

        if rag_result.get('error'):
            return {
                'query': query,
                'response': f"Error retrieving context: {rag_result['error']}",
                'sources': [],
                'context_used': '',
                'error': rag_result['error']
            }

        # Generate response using the retrieved context
        response = await self.generate_response(
            query=query,
            context_chunks=rag_result['context_chunks'],
            user_profile=user_profile,
            selected_text=selected_text
        )

        # Add RAG-specific metadata to the response
        response['retrieval_metadata'] = {
            'retrieval_count': rag_result['retrieval_count'],
            'doc_path_filter': doc_path_filter,
            'retrieval_limit': limit
        }

        return response


# Global instance
rag_agent = RAGAgent()


async def generate_response(query: str, context_chunks: List[Dict[str, Any]],
                          user_profile: Optional[Dict[str, Any]] = None,
                          selected_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate a response
    """
    return await rag_agent.generate_response(query, context_chunks, user_profile, selected_text)


async def query_with_rag(query: str, doc_path_filter: Optional[str] = None,
                        user_profile: Optional[Dict[str, Any]] = None,
                        selected_text: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """
    Convenience function for complete RAG query
    """
    return await rag_agent.query_with_rag(query, doc_path_filter, user_profile, selected_text, limit)