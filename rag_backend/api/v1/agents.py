from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from ...agents.openai_agent_integration import OpenAIAgent

router = APIRouter(tags=["agents"])

# Request models for each subagent
class ROS2CodeGeneratorRequest(BaseModel):
    urdf_path: str
    target_controller: str
    robot_joints: list
    node_name: str
    additional_requirements: Optional[str] = ""

class GazeboSceneCreatorRequest(BaseModel):
    robot_model_path: str
    environment_type: str
    objects: list
    lighting: Optional[str] = "default"
    physics_properties: Optional[dict] = {}

class QuizGeneratorRequest(BaseModel):
    topic: str
    difficulty_level: str
    question_count: int
    question_types: list
    learning_objectives: list

# Response model
class AgentResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/agents/ros2-code-generator", response_model=AgentResponse)
async def ros2_code_generator(request: ROS2CodeGeneratorRequest):
    """Generate ROS2 code based on specifications"""
    try:
        agent = OpenAIAgent()
        result = await agent.generate_ros2_code(
            urdf_path=request.urdf_path,
            target_controller=request.target_controller,
            robot_joints=request.robot_joints,
            node_name=request.node_name,
            additional_requirements=request.additional_requirements
        )
        return AgentResponse(success=True, result=result)
    except Exception as e:
        return AgentResponse(success=False, error=str(e))

@router.post("/agents/gazebo-scene-creator", response_model=AgentResponse)
async def gazebo_scene_creator(request: GazeboSceneCreatorRequest):
    """Create Gazebo scene based on specifications"""
    try:
        agent = OpenAIAgent()
        result = await agent.create_gazebo_scene(
            robot_model_path=request.robot_model_path,
            environment_type=request.environment_type,
            objects=request.objects,
            lighting=request.lighting,
            physics_properties=request.physics_properties
        )
        return AgentResponse(success=True, result=result)
    except Exception as e:
        return AgentResponse(success=False, error=str(e))

@router.post("/agents/quiz-generator", response_model=AgentResponse)
async def quiz_generator(request: QuizGeneratorRequest):
    """Generate quiz based on specifications"""
    try:
        agent = OpenAIAgent()
        result = await agent.generate_quiz(
            topic=request.topic,
            difficulty_level=request.difficulty_level,
            question_count=request.question_count,
            question_types=request.question_types,
            learning_objectives=request.learning_objectives
        )
        return AgentResponse(success=True, result=result)
    except Exception as e:
        return AgentResponse(success=False, error=str(e))

# Include the router in the main app
def register_agents_router(app):
    """Helper function to register the agents router"""
    app.include_router(router, prefix="/api/v1")