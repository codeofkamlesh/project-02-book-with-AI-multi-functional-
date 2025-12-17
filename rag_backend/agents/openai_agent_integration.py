"""
OpenAI Agent Integration for the Physical AI & Humanoid Robotics RAG system.
Handles OpenAI API calls for RAG, personalization, and translation.
"""
import asyncio
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel


class OpenAIAgent:
    """
    Integration layer for OpenAI API calls including RAG, personalization, and translation
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # For testing purposes, we'll create a mock client when API key is not available
            self.client = None
            self.mock_mode = True
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            self.mock_mode = False

    async def generate_rag_response(
        self,
        query: str,
        context: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a RAG response based on query and context
        """
        try:
            # Customize prompt based on user profile if available
            if user_profile:
                complexity_modifier = self._get_complexity_modifier(user_profile)
                prompt_instruction = f"Answer the question considering the user has a {complexity_modifier} background in robotics and AI."
            else:
                prompt_instruction = "Answer the question based on the provided context."

            system_message = f"""You are an expert assistant for the Physical AI & Humanoid Robotics book. {prompt_instruction}

Provide accurate answers based solely on the provided context. Do not hallucinate or provide information not present in the context. If the answer is not available in the context, say so explicitly.

Context:
{context}
"""

            user_message = f"Question: {query}\n\nProvide a comprehensive answer based on the context above. Include relevant citations to the source materials when possible."

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for balanced performance and cost
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent, fact-based answers
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating RAG response: {str(e)}")
            raise

    async def personalize_content(
        self,
        content: str,
        user_profile: Dict[str, Any],
        mode: str = "simpler"
    ) -> str:
        """
        Personalize content based on user profile and requested mode
        """
        try:
            # Determine personalization instruction based on mode
            mode_instructions = {
                "simpler": "Rewrite the content to be more accessible for beginners, with simplified explanations and more examples.",
                "advanced": "Rewrite the content to be more technical and detailed, with advanced concepts and deeper explanations.",
                "visual": "Rewrite the content to emphasize visual elements and diagrams, with more descriptive explanations of visual components.",
                "code-heavy": "Rewrite the content to include more code examples, implementation details, and technical specifications."
            }

            personalization_instruction = mode_instructions.get(mode, mode_instructions["simpler"])

            system_message = f"""You are an expert content personalization assistant for the Physical AI & Humanoid Robotics book.
{personalization_instruction}

The user profile indicates:
- Software background: {user_profile.get('software_background', {})}
- Hardware background: {user_profile.get('hardware_background', {})}

Maintain all original facts and information from the source content, but adapt the presentation, complexity, and examples to match the user's background and the requested mode.
"""

            user_message = f"""Source content:\n{content}\n\nRewrite the content according to the personalization requirements while preserving all original facts and information."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,  # Slightly higher for creative rewriting
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error personalizing content: {str(e)}")
            raise

    async def translate_to_urdu(
        self,
        text: str
    ) -> str:
        """
        Translate English text to Urdu
        """
        try:
            if self.mock_mode:
                # Return a mock translation for testing purposes
                # In a real implementation, this would call the OpenAI API
                return f"**[URDU MOCK TRANSLATION]**\n\n{text}\n\n**[END MOCK TRANSLATION]**"

            system_message = """Translate the following technical educational content accurately into Urdu. Preserve all headings, section structure, and technical terms. Do not translate code blocks, file paths, commands, or diagram labels — keep them in English. Return only the translated Markdown."""

            user_message = f"Translate the following text to Urdu:\n\n{text}"

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini as specified
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for accuracy
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error translating to Urdu: {str(e)}")
            raise

    def _get_complexity_modifier(self, user_profile: Dict[str, Any]) -> str:
        """
        Determine complexity modifier based on user profile
        """
        software_level = user_profile.get("software_background", {}).get("level", "intermediate")
        hardware_experience = user_profile.get("hardware_background", {}).get("experience", "basic robotics")

        # Map profile to complexity level
        if software_level in ["advanced"] or hardware_experience in ["ROS experience"]:
            return "advanced"
        elif software_level in ["intermediate"] or hardware_experience in ["Jetson/embedded"]:
            return "intermediate"
        else:
            return "beginner-friendly"


    async def generate_ros2_code(
        self,
        urdf_path: str,
        target_controller: str,
        robot_joints: list,
        node_name: str,
        additional_requirements: str = ""
    ) -> Dict[str, str]:
        """
        Generate ROS2 code based on specifications
        """
        try:
            system_message = """You are an expert ROS2 developer. Generate complete, working ROS2 code based on the provided specifications.
            Follow ROS2 Humble Hawksbill conventions and best practices. Include proper error handling, logging, and documentation.
            Generate the following outputs:
            1. A complete rclpy node skeleton
            2. A launch file to start the node
            3. A specification for unit tests
            4. Inline documentation and comments"""

            user_message = f"""Generate ROS2 code with the following specifications:
- URDF path: {urdf_path}
- Target controller: {target_controller}
- Robot joints: {robot_joints}
- Node name: {node_name}
- Additional requirements: {additional_requirements}

Provide the output as separate code blocks for each component."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=3000
            )

            # In a real implementation, we would parse the response to extract the different components
            # For now, we'll return the full response
            return {
                "node_skeleton": response.choices[0].message.content,
                "launch_file": "# Launch file would be generated here based on the node",
                "tests_spec": "# Test specifications would be generated here",
                "documentation": "# Documentation would be extracted from the response"
            }

        except Exception as e:
            print(f"Error generating ROS2 code: {str(e)}")
            raise

    async def create_gazebo_scene(
        self,
        robot_model_path: str,
        environment_type: str,
        objects: list,
        lighting: str = "default",
        physics_properties: dict = None
    ) -> Dict[str, str]:
        """
        Create Gazebo scene based on specifications
        """
        try:
            if physics_properties is None:
                physics_properties = {}

            system_message = """You are an expert Gazebo simulation developer. Create a complete Gazebo world file based on the provided specifications.
            Follow SDF format standards and Gazebo Harmonic conventions. Include proper lighting, physics properties, and object placement."""

            user_message = f"""Create a Gazebo scene with the following specifications:
- Robot model path: {robot_model_path}
- Environment type: {environment_type}
- Objects to include: {objects}
- Lighting: {lighting}
- Physics properties: {physics_properties}

Provide the output as a complete SDF world file."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            return {
                "world_file": response.choices[0].message.content,
                "config": "# Configuration file would be generated here",
                "documentation": "# Documentation for the scene would be provided here"
            }

        except Exception as e:
            print(f"Error creating Gazebo scene: {str(e)}")
            raise

    async def generate_quiz(
        self,
        topic: str,
        difficulty_level: str,
        question_count: int,
        question_types: list,
        learning_objectives: list
    ) -> Dict[str, Any]:
        """
        Generate quiz based on specifications
        """
        try:
            system_message = """You are an expert educator creating quizzes for the Physical AI & Humanoid Robotics book.
            Generate questions that align with the learning objectives and match the specified difficulty level and types."""

            user_message = f"""Generate a quiz with the following specifications:
- Topic: {topic}
- Difficulty level: {difficulty_level}
- Number of questions: {question_count}
- Question types: {question_types}
- Learning objectives: {learning_objectives}

Provide the quiz with questions, answers, and explanations."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.4,
                max_tokens=2500
            )

            return {
                "questions": response.choices[0].message.content,
                "answers": "Answers would be extracted from the response",
                "explanations": "Explanations would be provided for each answer",
                "scoring_guide": "Scoring guide would be generated based on difficulty"
            }

        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        agent = OpenAIAgent()

        # Test RAG response
        query = "What are the main modules covered in this Physical AI & Humanoid Robotics book?"
        context = """This book follows a 4-model architecture:
1. ROS2 Foundations - Core concepts of Robot Operating System 2
2. Simulation - Gazebo and Unity environments for robot simulation
3. NVIDIA Isaac - Isaac Sim and Isaac ROS for perception and control
4. Vision-Language-Action (VLA) - Multimodal AI for humanoid control"""

        response = await agent.generate_rag_response(query, context)
        print(f"RAG Response: {response}")

        # Test personalization
        content = """ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms."""

        user_profile = {
            "software_background": {"level": "beginner", "languages": ["Python"]},
            "hardware_background": {"experience": "none"}
        }

        personalized = await agent.personalize_content(content, user_profile, "simpler")
        print(f"Personalized content: {personalized}")

        # Test translation
        urdu_translation = await agent.translate_to_urdu("Hello, this is a test of the Urdu translation feature.")
        print(f"Urdu translation: {urdu_translation}")

        # Test subagents
        ros2_result = await agent.generate_ros2_code(
            urdf_path="/path/to/robot.urdf",
            target_controller="position_controllers/JointGroupPositionController",
            robot_joints=["joint1", "joint2"],
            node_name="test_controller",
            additional_requirements="publish joint states"
        )
        print(f"ROS2 code generation result: {ros2_result}")

    # Run the test
    asyncio.run(test_agent())