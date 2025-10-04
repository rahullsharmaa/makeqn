from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from supabase import create_client, Client
import google.generativeai as genai
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase connection
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Gemini AI configuration with round-robin keys
GEMINI_API_KEYS = os.environ.get('GEMINI_API_KEYS', '').split(',')
GEMINI_API_KEYS = [key.strip() for key in GEMINI_API_KEYS if key.strip()]

# Track current key index and failed keys
current_key_index = 0
failed_keys = set()

def sanitize_gemini_json(raw_output: str) -> str:
    """Sanitize and clean Gemini API JSON response to handle malformed JSON"""
    if not raw_output or not raw_output.strip():
        raise ValueError("Empty response from Gemini API")
    
    # Remove markdown code blocks and extra formatting
    cleaned = re.sub(r"```json\s*", "", raw_output)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL)
    
    # Find JSON object boundaries
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    
    if start == -1 or end == -1:
        raise ValueError("No valid JSON object found in response")
    
    # Extract the JSON part
    json_str = cleaned[start:end + 1]
    
    # Fix common JSON issues
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    # Fix unterminated strings by ensuring proper quote matching
    # This is a basic attempt - for production, consider more sophisticated parsing
    json_str = json_str.strip()
    
    # Ensure the JSON ends properly
    if not json_str.endswith('}'):
        json_str += '}'
    
    return json_str

def robust_parse_json(response_text: str) -> dict:
    """Robustly parse Gemini JSON response with error recovery"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # First, try direct parsing
            if attempt == 0:
                return json.loads(response_text.strip())
            
            # If that fails, try sanitizing
            clean_json = sanitize_gemini_json(response_text)
            return json.loads(clean_json)
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries - 1:
                # Log the error for debugging
                print(f"JSON parsing failed after {max_retries} attempts. Raw response: {response_text[:500]}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse AI response as JSON after multiple attempts: {str(e)}"
                )
            continue
    
    # Should never reach here, but just in case
    raise HTTPException(status_code=500, detail="Unexpected error in JSON parsing")

def get_next_working_gemini_key():
    """Get the next working Gemini API key using round-robin"""
    global current_key_index
    
    if not GEMINI_API_KEYS:
        raise HTTPException(status_code=500, detail="No Gemini API keys configured")
    
    # Remove failed keys from available keys
    available_keys = [key for key in GEMINI_API_KEYS if key not in failed_keys]
    
    if not available_keys:
        # Reset failed keys if all keys have failed (maybe quotas reset)
        failed_keys.clear()
        available_keys = GEMINI_API_KEYS
    
    # Use round-robin to select next key
    key = available_keys[current_key_index % len(available_keys)]
    current_key_index = (current_key_index + 1) % len(available_keys)
    
    return key

def create_gemini_model_with_key(api_key: str):
    """Create a Gemini model with the specified API key"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

# Create the main app
app = FastAPI(title="Question Maker API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic models
class ExamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class CourseResponse(BaseModel):
    id: str
    exam_id: str
    name: str
    description: Optional[str] = None

class SubjectResponse(BaseModel):
    id: str
    course_id: str
    name: str
    description: Optional[str] = None

class UnitResponse(BaseModel):
    id: str
    subject_id: str
    name: str
    description: Optional[str] = None

class ChapterResponse(BaseModel):
    id: str
    unit_id: str
    name: str
    description: Optional[str] = None

class TopicResponse(BaseModel):
    id: str
    chapter_id: str
    name: str
    description: Optional[str] = None
    weightage: Optional[float] = None

class PartResponse(BaseModel):
    id: str
    part_name: str
    course_id: str

class SlotResponse(BaseModel):
    id: str
    slot_name: str
    course_id: str

class QuestionRequest(BaseModel):
    topic_id: str
    question_type: str  # MCQ, MSQ, NAT, SUB
    part_id: Optional[str] = None
    slot_id: Optional[str] = None
    correct_marks: Optional[float] = None
    incorrect_marks: Optional[float] = None
    skipped_marks: Optional[float] = None
    time_minutes: Optional[float] = None

class GeneratedQuestion(BaseModel):
    id: str
    topic_id: str
    topic_name: str
    question_statement: str
    question_type: str
    options: Optional[List[str]] = None
    answer: str
    solution: str
    difficulty_level: str
    part_id: Optional[str] = None
    slot_id: Optional[str] = None
    created_at: datetime

# New models for enhanced functionality
class AutoGenerationConfig(BaseModel):
    correct_marks: float
    incorrect_marks: float
    skipped_marks: float
    time_minutes: float
    total_questions: int

class AutoGenerationSession(BaseModel):
    id: str
    exam_id: str
    course_id: str
    config: AutoGenerationConfig
    current_subject_idx: int = 0
    current_unit_idx: int = 0
    current_chapter_idx: int = 0
    current_topic_idx: int = 0
    questions_generated: int = 0
    questions_target: int
    is_paused: bool = False
    is_completed: bool = False
    generation_mode: str = "new_questions"  # "new_questions" or "pyq_solutions"
    created_at: datetime
    updated_at: datetime

class TopicWithWeightage(BaseModel):
    id: str
    name: str
    weightage: Optional[float] = None
    chapter_id: str
    chapter_name: str
    unit_id: str
    unit_name: str
    subject_id: str
    subject_name: str
    estimated_questions: int = 0

class AutoGenerationProgress(BaseModel):
    session_id: str
    progress_percentage: float
    current_topic: Optional[str] = None
    questions_generated: int
    questions_target: int
    estimated_time_remaining: Optional[float] = None
    can_pause: bool = True

class PYQSolutionRequest(BaseModel):
    topic_id: str
    question_statement: str
    options: Optional[List[str]] = None
    question_type: str

class PYQSolutionByIdRequest(BaseModel):
    question_id: str

class PYQSolutionResponse(BaseModel):
    question_statement: str
    answer: str
    solution: str
    confidence_level: str

class GeneratedSolution(BaseModel):
    question_id: str
    question_statement: str
    answer: str
    solution: str
    confidence_level: str

class CoursePYQSolutionRequest(BaseModel):
    course_id: str
    
class PYQSolutionProgress(BaseModel):
    total_questions: int
    processed_questions: int
    successful_solutions: int
    failed_solutions: int
    current_question_id: Optional[str] = None
    is_completed: bool = False
    error_message: Optional[str] = None

# API Routes

@api_router.get("/")
async def root():
    return {"message": "Question Maker API is running"}

@api_router.get("/exams", response_model=List[ExamResponse])
async def get_exams():
    """Get all available exams"""
    try:
        result = supabase.table("exams").select("*").execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching exams: {str(e)}")

@api_router.get("/courses/{exam_id}", response_model=List[CourseResponse])
async def get_courses(exam_id: str):
    """Get courses for a specific exam"""
    try:
        result = supabase.table("courses").select("*").eq("exam_id", exam_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses: {str(e)}")

@api_router.get("/subjects/{course_id}", response_model=List[SubjectResponse])
async def get_subjects(course_id: str):
    """Get subjects for a specific course"""
    try:
        result = supabase.table("subjects").select("*").eq("course_id", course_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subjects: {str(e)}")

@api_router.get("/units/{subject_id}", response_model=List[UnitResponse])
async def get_units(subject_id: str):
    """Get units for a specific subject"""
    try:
        result = supabase.table("units").select("*").eq("subject_id", subject_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching units: {str(e)}")

@api_router.get("/chapters/{unit_id}", response_model=List[ChapterResponse])
async def get_chapters(unit_id: str):
    """Get chapters for a specific unit"""
    try:
        result = supabase.table("chapters").select("*").eq("unit_id", unit_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chapters: {str(e)}")

@api_router.get("/topics/{chapter_id}", response_model=List[TopicResponse])
async def get_topics(chapter_id: str):
    """Get topics for a specific chapter"""
    try:
        result = supabase.table("topics").select("*").eq("chapter_id", chapter_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching topics: {str(e)}")

@api_router.get("/parts/{course_id}", response_model=List[PartResponse])
async def get_parts(course_id: str):
    """Get parts for a specific course"""
    try:
        result = supabase.table("parts").select("*").eq("course_id", course_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parts: {str(e)}")

@api_router.get("/slots/{course_id}", response_model=List[SlotResponse])
async def get_slots(course_id: str):
    """Get slots for a specific course"""
    try:
        result = supabase.table("slots").select("*").eq("course_id", course_id).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching slots: {str(e)}")

@api_router.get("/existing-questions/{topic_id}")
async def get_existing_questions(topic_id: str):
    """Get existing questions for a topic for reference"""
    try:
        result = supabase.table("questions_topic_wise").select("id, question_statement, options, answer, solution, question_type").eq("topic_id", topic_id).limit(10).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching existing questions: {str(e)}")

@api_router.get("/generated-questions/{topic_id}")
async def get_generated_questions(topic_id: str):
    """Get previously generated questions for a topic"""
    try:
        result = supabase.table("new_questions").select("*").eq("topic_id", topic_id).order("created_at", desc=True).limit(10).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching generated questions: {str(e)}")

# Model for updating question solutions
class UpdateQuestionSolution(BaseModel):
    question_id: str
    answer: str 
    solution: str
    confidence_level: str

@api_router.patch("/update-question-solution")
async def update_question_solution(request: UpdateQuestionSolution):
    """Update an existing question with generated solution"""
    try:
        # Try to update in questions_topic_wise table first
        result = supabase.table("questions_topic_wise").update({
            "answer": request.answer,
            "solution": request.solution,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", request.question_id).execute()
        
        if result.data:
            return {"message": "Question solution updated successfully", "question_id": request.question_id}
        
        # If not found in questions_topic_wise, try new_questions table
        result = supabase.table("new_questions").update({
            "answer": request.answer,
            "solution": request.solution,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", request.question_id).execute()
        
        if result.data:
            return {"message": "Question solution updated successfully", "question_id": request.question_id}
        
        # If not found in either table
        raise HTTPException(status_code=404, detail="Question not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating question solution: {str(e)}")
def validate_question_answer(question_type: str, options: List[str], answer: str) -> bool:
    """Validate that the question answer follows the rules"""
    if question_type == "MCQ":
        # MCQ should have exactly one correct answer
        try:
            answer_indices = [int(x.strip()) for x in answer.split(",") if x.strip().isdigit()]
            return len(answer_indices) == 1 and all(0 <= idx < len(options) for idx in answer_indices)
        except (ValueError, TypeError, AttributeError):
            return False
    elif question_type == "MSQ":
        # MSQ should have one or more correct answers
        try:
            answer_indices = [int(x.strip()) for x in answer.split(",") if x.strip().isdigit()]
            return len(answer_indices) >= 1 and all(0 <= idx < len(options) for idx in answer_indices)
        except (ValueError, TypeError, AttributeError):
            return False
    elif question_type == "NAT":
        # NAT should be a numerical value
        try:
            float(answer)
            return True
        except (ValueError, TypeError):
            return False
    elif question_type == "SUB":
        # SUB can be any text
        return len(answer.strip()) > 0
    return False

@api_router.get("/all-topics-with-weightage/{course_id}", response_model=List[TopicWithWeightage])
async def get_all_topics_with_weightage(course_id: str):
    """Get all topics with weightage information for a course"""
    try:
        # Get all subjects for the course
        subjects_result = supabase.table("subjects").select("*").eq("course_id", course_id).execute()
        all_topics = []
        
        for subject in subjects_result.data:
            # Get units for subject
            units_result = supabase.table("units").select("*").eq("subject_id", subject["id"]).execute()
            
            for unit in units_result.data:
                # Get chapters for unit
                chapters_result = supabase.table("chapters").select("*").eq("unit_id", unit["id"]).execute()
                
                for chapter in chapters_result.data:
                    # Get topics for chapter
                    topics_result = supabase.table("topics").select("*").eq("chapter_id", chapter["id"]).execute()
                    
                    for topic in topics_result.data:
                        all_topics.append(TopicWithWeightage(
                            id=topic["id"],
                            name=topic["name"],
                            weightage=topic.get("weightage", 0.0),
                            chapter_id=chapter["id"],
                            chapter_name=chapter["name"],
                            unit_id=unit["id"],
                            unit_name=unit["name"],
                            subject_id=subject["id"],
                            subject_name=subject["name"]
                        ))
        
        return all_topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching topics with weightage: {str(e)}")

@api_router.post("/auto-generation-session")
async def create_auto_generation_session(config: AutoGenerationConfig, exam_id: str, course_id: str, generation_mode: str = "new_questions"):
    """Create a new auto-generation session"""
    try:
        # Get all topics with weightage for the course
        topics = await get_all_topics_with_weightage(course_id)
        
        # Calculate questions per topic based on weightage
        total_weightage = sum(topic.weightage or 0 for topic in topics)
        if total_weightage == 0:
            # If no weightage, distribute equally
            questions_per_topic = max(1, config.total_questions // len(topics)) if topics else 0
            for topic in topics:
                topic.estimated_questions = questions_per_topic
        else:
            # Distribute based on weightage using proper rounding
            total_allocated = 0
            topics_with_questions = []
            
            for topic in topics:
                if topic.weightage and topic.weightage > 0:
                    # Calculate questions based on exact weightage percentage with proper rounding
                    topic_questions = max(1, round((topic.weightage / 100) * config.total_questions))
                else:
                    # Topics without weightage get minimum 1 question
                    topic_questions = 1
                
                topic.estimated_questions = topic_questions
                total_allocated += topic_questions
                topics_with_questions.append(topic)
            
            # Adjust if total doesn't match exactly due to rounding
            difference = config.total_questions - total_allocated
            if difference != 0 and topics_with_questions:
                # Find topic with highest weightage to adjust
                max_weightage_topic = max(topics_with_questions, key=lambda t: t.weightage or 0)
                max_weightage_topic.estimated_questions = max(1, max_weightage_topic.estimated_questions + difference)
        
        session_id = str(uuid.uuid4())
        session = AutoGenerationSession(
            id=session_id,
            exam_id=exam_id,
            course_id=course_id,
            config=config,
            questions_target=config.total_questions,
            generation_mode=generation_mode,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # For now, we'll return the session. In a real implementation, you'd store this in a sessions table
        return {"session_id": session_id, "session": session, "topics": topics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating auto-generation session: {str(e)}")

@api_router.post("/generate-pyq-solution", response_model=PYQSolutionResponse)
async def generate_pyq_solution(request: PYQSolutionRequest):
    """Generate answer and solution for a PYQ question"""
    try:
        # Get topic information for context
        topic_result = supabase.table("topics").select("*").eq("id", request.topic_id).execute()
        if not topic_result.data:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic = topic_result.data[0]
        
        # Get chapter and course information for better context
        chapter_result = supabase.table("chapters").select("*").eq("id", topic["chapter_id"]).execute()
        chapter = chapter_result.data[0] if chapter_result.data else {}
        
        # Get topic notes for context (as requested by user)
        topic_notes = topic.get('notes', '').strip()
        
        # Create prompt for Gemini to solve the PYQ
        prompt = f"""
You are an expert educator and question solver. Analyze the following previous year question and provide the correct answer and detailed solution.

Topic: {topic['name']}
Chapter: {chapter.get('name', '')}
Question Type: {request.question_type}

{f'Topic Notes (Use these concepts and methods from the chapter): {topic_notes}' if topic_notes else ''}

Question: {request.question_statement}

{f'Options: {request.options}' if request.options else ''}

Your task:
1. Carefully analyze the question and determine the correct answer
2. Provide a step-by-step solution explaining the reasoning
3. Use the concepts from the topic notes provided above when solving
4. Double-check your work to ensure accuracy

Requirements:
- For MCQ: Provide the correct option index (0-3)
- For MSQ: Provide comma-separated correct option indices
- For NAT: Provide the numerical answer
- For SUB: Provide a comprehensive answer

Respond in the following JSON format:
{{
    "answer": "Your answer here (following the format rules above)",
    "solution": "Detailed step-by-step solution with clear explanations using concepts from the topic notes",
    "confidence_level": "High/Medium/Low - your confidence in this solution"
}}
"""

        # Generate response from Gemini with round-robin key handling
        max_retries = len(GEMINI_API_KEYS)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get next working API key
                current_api_key = get_next_working_gemini_key()
                
                # Create model with current key
                model = create_gemini_model_with_key(current_api_key)
                
                # Define JSON schema for PYQ solution output
                response_schema = genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "answer": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "solution": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "confidence_level": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["answer", "solution", "confidence_level"]
                )
                
                # Configure generation for structured JSON output with schema
                generation_config = genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.3  # Lower temperature for more accurate answers
                )
                
                # Generate content with structured output
                response = model.generate_content(prompt, generation_config=generation_config)
                break
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a quota/authentication error
                if "quota" in error_str or "429" in error_str or "exceeded" in error_str or "invalid api key" in error_str:
                    failed_keys.add(current_api_key)
                    if attempt == max_retries - 1:
                        raise HTTPException(status_code=429, detail=f"All Gemini API keys exhausted. Last error: {str(e)}")
                    continue
                else:
                    raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
        
        if last_error and 'response' not in locals():
            raise HTTPException(status_code=500, detail=f"Failed after all retries: {str(last_error)}")
        
        # Parse the JSON response using robust parsing
        try:
            response_text = response.text.strip()
            solution_data = robust_parse_json(response_text)
        except HTTPException:
            raise

        # Validate the solution
        if not isinstance(solution_data, dict):
            raise HTTPException(status_code=500, detail="AI response is not a valid object")
        
        # Create response
        pyq_solution = PYQSolutionResponse(
            question_statement=request.question_statement,
            answer=solution_data.get("answer", ""),
            solution=solution_data.get("solution", ""),
            confidence_level=solution_data.get("confidence_level", "Medium")
        )
        
        return pyq_solution
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PYQ solution: {str(e)}")

@api_router.post("/generate-pyq-solution-by-id", response_model=GeneratedSolution)
async def generate_pyq_solution_by_id(request: PYQSolutionByIdRequest):
    """Generate solution for an existing PYQ question"""
    try:
        # Get the question details from questions_topic_wise table first
        question_result = supabase.table("questions_topic_wise").select("*").eq("id", request.question_id).execute()
        question = None
        source_table = "questions_topic_wise"
        
        if question_result.data:
            question = question_result.data[0]
        else:
            # If not found in questions_topic_wise, try new_questions table  
            question_result = supabase.table("new_questions").select("*").eq("id", request.question_id).execute()
            if question_result.data:
                question = question_result.data[0]
                source_table = "new_questions"
            else:
                raise HTTPException(status_code=404, detail="Question not found in either questions_topic_wise or new_questions table")
        
        # Get topic information for context
        topic_result = supabase.table("topics").select("*").eq("id", question["topic_id"]).execute()
        if not topic_result.data:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic = topic_result.data[0]
        
        # Get chapter and course information for better context
        chapter_result = supabase.table("chapters").select("*").eq("id", topic["chapter_id"]).execute()
        chapter = chapter_result.data[0] if chapter_result.data else {}
        
        # Get topic notes for context (as requested by user)
        topic_notes = topic.get('notes', '').strip()
        
        # Create prompt for Gemini to solve the PYQ
        prompt = f"""
You are an expert educator and question solver. Analyze the following previous year question and provide the correct answer and detailed solution.

Topic: {topic['name']}
Chapter: {chapter.get('name', '')}
Question Type: {question['question_type']}

{f'Topic Notes (Use these concepts and methods from the chapter): {topic_notes}' if topic_notes else ''}

Question: {question['question_statement']}

{f'Options: {question.get("options", [])}' if question.get("options") else ''}

Your task:
1. Carefully analyze the question and determine the correct answer
2. Provide a step-by-step solution explaining the reasoning
3. Use the concepts from the topic notes provided above when solving
4. Double-check your work to ensure accuracy

Requirements:
- For MCQ: Provide the correct option index (0-3)
- For MSQ: Provide comma-separated correct option indices
- For NAT: Provide the numerical answer
- For SUB: Provide a comprehensive answer

Respond in the following JSON format:
{{
    "answer": "Your answer here (following the format rules above)",
    "solution": "Detailed step-by-step solution with clear explanations using concepts from the topic notes",
    "confidence_level": "High/Medium/Low - your confidence in this solution"
}}
"""

        # Generate response from Gemini with round-robin key handling
        max_retries = len(GEMINI_API_KEYS)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get next working API key
                current_api_key = get_next_working_gemini_key()
                
                # Create model with current key
                model = create_gemini_model_with_key(current_api_key)
                
                # Define JSON schema for PYQ solution output
                response_schema = genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "answer": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "solution": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "confidence_level": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["answer", "solution", "confidence_level"]
                )
                
                # Configure generation for structured JSON output with schema
                generation_config = genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.3  # Lower temperature for more accurate answers
                )
                
                # Generate content with structured output
                response = model.generate_content(prompt, generation_config=generation_config)
                break
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a quota/authentication error
                if "quota" in error_str or "429" in error_str or "exceeded" in error_str or "invalid api key" in error_str:
                    failed_keys.add(current_api_key)
                    if attempt == max_retries - 1:
                        raise HTTPException(status_code=429, detail=f"All Gemini API keys exhausted. Last error: {str(e)}")
                    continue
                else:
                    raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
        
        if last_error and 'response' not in locals():
            raise HTTPException(status_code=500, detail=f"Failed after all retries: {str(last_error)}")
        
        # Parse the JSON response using robust parsing
        try:
            response_text = response.text.strip()
            solution_data = robust_parse_json(response_text)
        except HTTPException:
            raise

        # Validate the solution
        if not isinstance(solution_data, dict):
            raise HTTPException(status_code=500, detail="AI response is not a valid object")
        
        # Create response
        generated_solution = GeneratedSolution(
            question_id=request.question_id,
            question_statement=question["question_statement"],
            answer=solution_data.get("answer", ""),
            solution=solution_data.get("solution", ""),
            confidence_level=solution_data.get("confidence_level", "Medium")
        )
        
        return generated_solution
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PYQ solution: {str(e)}")

@api_router.post("/generate-course-pyq-solutions", response_model=PYQSolutionProgress)
async def generate_course_pyq_solutions(request: CoursePYQSolutionRequest):
    """Generate solutions for all PYQ questions in a course"""
    try:
        # Get all topics for the course that have PYQ questions without solutions
        pyq_questions_query = """
            SELECT q.*, t.name as topic_name, t.notes as topic_notes
            FROM questions_topic_wise q
            JOIN topics t ON q.topic_id = t.id
            JOIN chapters c ON t.chapter_id = c.id
            JOIN units u ON c.unit_id = u.id
            JOIN subjects s ON u.subject_id = s.id
            WHERE s.course_id = %s 
            AND (q.solution IS NULL OR q.solution = '' OR q.solution_done = false)
            ORDER BY t.name, q.question_statement
            LIMIT 100
        """
        
        # Use raw SQL to get the questions with proper joins
        try:
            # Get questions through the API - first get all topics for the course
            topics_result = supabase.rpc('get_course_topics_with_questions', {
                'p_course_id': request.course_id
            }).execute()
            
            if not topics_result.data:
                # Fallback: get topics directly and then find questions
                course_topics = supabase.table("topics").select("""
                    id, name, notes,
                    chapters!inner(
                        units!inner(
                            subjects!inner(
                                course_id
                            )
                        )
                    )
                """).eq("chapters.units.subjects.course_id", request.course_id).execute()
                
                if not course_topics.data:
                    return PYQSolutionProgress(
                        total_questions=0,
                        processed_questions=0,
                        successful_solutions=0,
                        failed_solutions=0,
                        is_completed=True,
                        error_message="No topics found for this course"
                    )
            
            # Get all PYQ questions that need solutions
            all_questions = []
            topic_ids = [topic['id'] for topic in course_topics.data] if course_topics.data else []
            
            for topic_id in topic_ids:
                questions_result = supabase.table("questions_topic_wise").select("*").eq("topic_id", topic_id).execute()
                for question in questions_result.data:
                    # Check if solution is missing or solution_done is false
                    if (not question.get('solution') or 
                        question.get('solution', '').strip() == '' or 
                        not question.get('solution_done', False)):
                        
                        # Add topic info to question
                        topic_info = next((t for t in course_topics.data if t['id'] == topic_id), {})
                        question['topic_name'] = topic_info.get('name', '')
                        question['topic_notes'] = topic_info.get('notes', '')
                        all_questions.append(question)
            
        except Exception as e:
            # Fallback approach if RPC doesn't exist
            # Get all questions for the course topics
            all_questions = []
            
            # First get topics for the course
            topics_query = supabase.table("topics").select("""
                *,
                chapters!inner(
                    units!inner(
                        subjects!inner(
                            course_id
                        )
                    )
                )
            """).eq("chapters.units.subjects.course_id", request.course_id).execute()
            
            for topic in topics_query.data:
                # Get questions for each topic that need solutions
                questions_result = supabase.table("questions_topic_wise").select("*").eq("topic_id", topic['id']).execute()
                
                for question in questions_result.data:
                    # Check if solution is missing or solution_done is false
                    if (not question.get('solution') or 
                        question.get('solution', '').strip() == '' or 
                        not question.get('solution_done', False)):
                        
                        question['topic_name'] = topic.get('name', '')
                        question['topic_notes'] = topic.get('notes', '')
                        all_questions.append(question)
        
        total_questions = len(all_questions)
        
        if total_questions == 0:
            return PYQSolutionProgress(
                total_questions=0,
                processed_questions=0,
                successful_solutions=0,
                failed_solutions=0,
                is_completed=True,
                error_message="No PYQ questions need solutions in this course"
            )
        
        # Process questions one by one
        successful_solutions = 0
        failed_solutions = 0
        
        for i, question in enumerate(all_questions):
            try:
                # Create a solution request
                solution_request = PYQSolutionRequest(
                    topic_id=question['topic_id'],
                    question_statement=question['question_statement'],
                    options=question.get('options', []),
                    question_type=question.get('question_type', 'MCQ')
                )
                
                # Generate solution using the existing endpoint logic
                topic_result = supabase.table("topics").select("*").eq("id", question['topic_id']).execute()
                if not topic_result.data:
                    failed_solutions += 1
                    continue
                
                topic = topic_result.data[0]
                
                # Get chapter info
                chapter_result = supabase.table("chapters").select("*").eq("id", topic["chapter_id"]).execute()
                chapter = chapter_result.data[0] if chapter_result.data else {}
                
                # Get topic notes for context
                topic_notes = topic.get('notes', '').strip()
                
                # Create prompt for Gemini
                prompt = f"""
You are an expert educator and question solver. Analyze the following previous year question and provide the correct answer and detailed solution.

Topic: {topic['name']}
Chapter: {chapter.get('name', '')}
Question Type: {solution_request.question_type}

{f'Topic Notes (Use these concepts and methods from the chapter): {topic_notes}' if topic_notes else ''}

Question: {solution_request.question_statement}

{f'Options: {solution_request.options}' if solution_request.options else ''}

Your task:
1. Carefully analyze the question and determine the correct answer
2. Provide a step-by-step solution explaining the reasoning
3. Use the concepts from the topic notes provided above when solving
4. Double-check your work to ensure accuracy

Requirements:
- For MCQ: Provide the correct option index (0-3)
- For MSQ: Provide comma-separated correct option indices
- For NAT: Provide the numerical answer
- For SUB: Provide a comprehensive answer

Respond in the following JSON format:
{{
    "answer": "Your answer here (following the format rules above)",
    "solution": "Detailed step-by-step solution with clear explanations using concepts from the topic notes",
    "confidence_level": "High/Medium/Low - your confidence in this solution"
}}
"""

                # Generate response from Gemini
                max_retries = len(GEMINI_API_KEYS)
                last_error = None
                solution_generated = False
                
                for attempt in range(max_retries):
                    try:
                        current_api_key = get_next_working_gemini_key()
                        model = create_gemini_model_with_key(current_api_key)
                        
                        # Define JSON schema
                        response_schema = genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "answer": genai.protos.Schema(type=genai.protos.Type.STRING),
                                "solution": genai.protos.Schema(type=genai.protos.Type.STRING),
                                "confidence_level": genai.protos.Schema(type=genai.protos.Type.STRING)
                            },
                            required=["answer", "solution", "confidence_level"]
                        )
                        
                        generation_config = genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=response_schema,
                            temperature=0.3
                        )
                        
                        response = model.generate_content(prompt, generation_config=generation_config)
                        
                        # Parse response using robust parsing
                        response_text = response.text.strip()
                        solution_data = robust_parse_json(response_text)
                        
                        # Update the question in the database with the solution
                        update_data = {
                            "answer": solution_data.get("answer", ""),
                            "solution": solution_data.get("solution", ""),
                            "solution_done": True,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        # Update the question in questions_topic_wise table
                        update_result = supabase.table("questions_topic_wise").update(update_data).eq("id", question['id']).execute()
                        
                        if update_result.data:
                            successful_solutions += 1
                            solution_generated = True
                            break
                        else:
                            raise Exception("Failed to update question in database")
                            
                    except Exception as e:
                        last_error = e
                        error_str = str(e).lower()
                        
                        if "quota" in error_str or "429" in error_str or "exceeded" in error_str or "invalid api key" in error_str:
                            failed_keys.add(current_api_key)
                            if attempt == max_retries - 1:
                                break
                            continue
                        else:
                            break
                
                if not solution_generated:
                    failed_solutions += 1
                
            except Exception as e:
                failed_solutions += 1
                print(f"Error processing question {question.get('id', 'unknown')}: {str(e)}")
            
            # For progress tracking, we could implement real-time updates here
            # For now, we'll just return final results
        
        return PYQSolutionProgress(
            total_questions=total_questions,
            processed_questions=total_questions,
            successful_solutions=successful_solutions,
            failed_solutions=failed_solutions,
            is_completed=True,
            error_message=f"Completed: {successful_solutions} successful, {failed_solutions} failed" if failed_solutions > 0 else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating course PYQ solutions: {str(e)}")

@api_router.post("/generate-question", response_model=GeneratedQuestion)
async def generate_question(request: QuestionRequest):
    """Generate a new question using Gemini AI"""
    try:
        # Get topic information
        topic_result = supabase.table("topics").select("*").eq("id", request.topic_id).execute()
        if not topic_result.data:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic = topic_result.data[0]
        
        # Get chapter information for context
        chapter_result = supabase.table("chapters").select("*").eq("id", topic["chapter_id"]).execute()
        chapter = chapter_result.data[0] if chapter_result.data else {}
        
        # Get unit information
        unit_result = supabase.table("units").select("*").eq("id", chapter.get("unit_id", "")).execute()
        unit = unit_result.data[0] if unit_result.data else {}
        
        # Get subject information
        subject_result = supabase.table("subjects").select("*").eq("id", unit.get("subject_id", "")).execute()
        subject = subject_result.data[0] if subject_result.data else {}
        
        # Get course information
        course_result = supabase.table("courses").select("*").eq("id", subject.get("course_id", "")).execute()
        course = course_result.data[0] if course_result.data else {}
        
        # Get exam information
        exam_result = supabase.table("exams").select("*").eq("id", course.get("exam_id", "")).execute()
        exam = exam_result.data[0] if exam_result.data else {}
        
        # Get existing questions for reference (but not to copy)
        existing_questions = supabase.table("questions_topic_wise").select("question_statement, options, question_type").eq("topic_id", request.topic_id).limit(5).execute()
        
        # Get previously generated questions to avoid repetition
        generated_questions = supabase.table("new_questions").select("question_statement").eq("topic_id", request.topic_id).limit(10).execute()
        
        # Create prompt for Gemini
        prompt = f"""
You are an expert question creator for educational content. Generate a {request.question_type} type question for the following topic:

EXAM CONTEXT:
- Exam: {exam.get('name', 'Unknown Exam')}
- Course: {course.get('name', 'Unknown Course')}
- Subject: {subject.get('name', 'Unknown Subject')}
- Unit: {unit.get('name', 'Unknown Unit')}
- Chapter: {chapter.get('name', 'Unknown Chapter')}
- Topic: {topic['name']}

IMPORTANT: Create questions appropriate for the {exam.get('name', 'exam')} difficulty level and {course.get('name', 'course')} standards. Keep the difficulty suitable for this specific exam and course context.

Topic Description: {topic.get('description', '')}

Question Type Rules:
- MCQ: Multiple Choice Question with exactly ONE correct answer (4 options)
- MSQ: Multiple Select Question with ONE OR MORE correct answers (4 options)
- NAT: Numerical Answer Type with a numerical answer (no options)
- SUB: Subjective question with descriptive answer (no options)

Context from existing questions (DO NOT COPY, use for inspiration only):
{json.dumps([q['question_statement'] for q in existing_questions.data[:3]], indent=2)}

Previously generated questions in this topic (AVOID similar content - generate something completely different):
{json.dumps([q['question_statement'] for q in generated_questions.data], indent=2)}

Requirements:
1. Generate a FRESH, ORIGINAL question that tests understanding of the topic
2. Make it educationally valuable and appropriately challenging for {exam.get('name', 'the exam')}
3. Ensure difficulty is suitable for {course.get('name', 'the course')} level
4. For MCQ/MSQ: Provide exactly 4 options with realistic distractors
5. Ensure the answer follows the question type rules strictly
6. Provide a detailed solution explanation with clear steps
7. AVOID any similarity with previously generated questions listed above

Please respond in the following JSON format:
{{
    "question_statement": "Your question here",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"] or null for NAT/SUB,
    "answer": "For MCQ: single number (0-3), for MSQ: comma-separated numbers (0,1,2), for NAT: numerical value, for SUB: descriptive answer",
    "solution": "Detailed step-by-step solution",
    "difficulty_level": "Easy/Medium/Hard"
}}
"""

        # Generate response from Gemini with round-robin key handling
        max_retries = len(GEMINI_API_KEYS)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get next working API key
                current_api_key = get_next_working_gemini_key()
                
                # Create model with current key
                model = create_gemini_model_with_key(current_api_key)
                
                # Define JSON schema for consistent output
                response_schema = genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "question_statement": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "options": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.STRING)
                        ),
                        "answer": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "solution": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "difficulty_level": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["question_statement", "answer", "solution", "difficulty_level"]
                )
                
                # Configure generation for structured JSON output with schema
                generation_config = genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.7
                )
                
                # Generate content with structured output
                response = model.generate_content(prompt, generation_config=generation_config)
                
                # If successful, break out of retry loop
                break
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a quota/authentication error
                if "quota" in error_str or "429" in error_str or "exceeded" in error_str or "invalid api key" in error_str:
                    # Mark current key as failed
                    failed_keys.add(current_api_key)
                    print(f"API key failed (quota/auth error), marked as failed: {current_api_key[:10]}...")
                    
                    # If this was the last attempt, raise the error
                    if attempt == max_retries - 1:
                        raise HTTPException(status_code=429, detail=f"All Gemini API keys exhausted. Last error: {str(e)}")
                    
                    # Continue to next key
                    continue
                else:
                    # For other errors, don't retry
                    raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
        
        if last_error and 'response' not in locals():
            raise HTTPException(status_code=500, detail=f"Failed after all retries: {str(last_error)}")
        
        # Parse the JSON response
        try:
            # Get response text
            response_text = response.text.strip()
            
            # Use robust JSON parsing for consistent handling
            generated_data = robust_parse_json(response_text)
            
        except HTTPException:
            raise

        # Handle case where Gemini returns an array instead of a single object
        if isinstance(generated_data, list):
            if len(generated_data) > 0:
                generated_data = generated_data[0]  # Take the first item
            else:
                raise HTTPException(status_code=500, detail="AI returned empty array response")
        
        # Ensure generated_data is a dictionary
        if not isinstance(generated_data, dict):
            raise HTTPException(status_code=500, detail=f"AI response is not a valid object. Got: {type(generated_data)}")
        
        # Validate the generated question
        options = generated_data.get("options", [])
        answer = generated_data.get("answer", "")
        
        if not validate_question_answer(request.question_type, options, answer):
            raise HTTPException(status_code=400, detail=f"Generated question doesn't meet {request.question_type} validation rules")

        # Create new question record
        new_question = {
            "id": str(uuid.uuid4()),
            "topic_id": request.topic_id,
            "topic_name": topic["name"],
            "question_statement": generated_data["question_statement"],
            "question_type": request.question_type,
            "options": options if request.question_type in ["MCQ", "MSQ"] else None,
            "answer": answer,
            "solution": generated_data["solution"],
            "difficulty_level": generated_data.get("difficulty_level", "Medium"),
            "part_id": request.part_id,
            "slot_id": request.slot_id,
            "correct_marks": request.correct_marks,
            "incorrect_marks": request.incorrect_marks,
            "skipped_marks": request.skipped_marks,
            "time_minutes": request.time_minutes,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Save to database with constraint handling
        try:
            result = supabase.table("new_questions").insert(new_question).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Error saving question to database")
                
        except Exception as db_error:
            # Check if it's a constraint violation for SUB or NAT questions
            error_str = str(db_error).lower()
            if "check constraint" in error_str and "question_type" in error_str:
                if request.question_type in ["SUB", "NAT"]:
                    # For SUB and NAT questions that fail constraint, save to questions_topic_wise table instead
                    try:
                        # Modify the new_question structure for questions_topic_wise table
                        question_for_topic_wise = {
                            "id": new_question["id"],
                            "topic_id": new_question["topic_id"],
                            "question_statement": new_question["question_statement"],
                            "question_type": new_question["question_type"],
                            "options": new_question["options"],
                            "answer": new_question["answer"],
                            "solution": new_question["solution"],
                            "difficulty_level": new_question["difficulty_level"],
                            "created_at": new_question["created_at"],
                            "updated_at": new_question["updated_at"]
                        }
                        
                        result = supabase.table("questions_topic_wise").insert(question_for_topic_wise).execute()
                        
                        if not result.data:
                            raise HTTPException(status_code=500, detail=f"Error saving {request.question_type} question to questions_topic_wise table")
                            
                        # Add a note that this was saved to alternate table
                        new_question["_saved_to_table"] = "questions_topic_wise"
                        
                    except Exception as fallback_error:
                        raise HTTPException(status_code=500, detail=f"Database constraint error for {request.question_type} questions. Primary table rejected due to constraint, fallback table also failed: {str(fallback_error)}")
                else:
                    raise HTTPException(status_code=500, detail=f"Database constraint error: {str(db_error)}")
            else:
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")

        return GeneratedQuestion(**new_question)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

@api_router.post("/save-question-manually")
async def save_question_manually(question_data: dict):
    """Save a manually created/reviewed question to the database"""
    try:
        # Always generate a new UUID to avoid conflicts
        new_id = str(uuid.uuid4())
        question_data["id"] = new_id
        question_data["created_at"] = datetime.now(timezone.utc).isoformat()
        question_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save to database
        result = supabase.table("new_questions").insert(question_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error saving question to database")
        
        return {"message": "Question saved successfully", "question_id": new_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving question: {str(e)}")

@api_router.post("/start-auto-generation")
async def start_auto_generation(
    exam_id: str,
    course_id: str, 
    config: AutoGenerationConfig,
    generation_mode: str = "new_questions"
):
    """Start automatic question generation process"""
    try:
        # Create session
        session_response = await create_auto_generation_session(config, exam_id, course_id, generation_mode)
        session_id = session_response["session_id"]
        topics = session_response["topics"]
        
        # Store session state (in a real app, you'd use a proper database table)
        # For now, we'll return the initial state
        
        return {
            "session_id": session_id,
            "total_topics": len(topics),
            "total_questions_planned": config.total_questions,
            "status": "ready_to_start",
            "message": "Auto-generation session created. Ready to start generating questions."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting auto-generation: {str(e)}")

@api_router.post("/auto-generate-next-question/{session_id}")
async def auto_generate_next_question(session_id: str):
    """Generate the next question in an auto-generation session"""
    try:
        # In a real implementation, you'd load the session state from database
        # For now, we'll return a placeholder response
        return {
            "message": "Auto-generation logic will be implemented in frontend",
            "session_id": session_id,
            "status": "use_frontend_logic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in auto-generation: {str(e)}")

@api_router.get("/auto-generation-progress/{session_id}")
async def get_auto_generation_progress(session_id: str):
    """Get progress of auto-generation session"""
    try:
        # In a real implementation, you'd load this from database
        return {
            "session_id": session_id,
            "message": "Progress tracking will be handled by frontend",
            "status": "use_frontend_logic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)