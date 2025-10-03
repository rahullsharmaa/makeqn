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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase connection
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Gemini AI configuration
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

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
        result = supabase.table("questions_topic_wise").select("question_statement, options, answer, solution, question_type").eq("topic_id", topic_id).limit(5).execute()
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

def validate_question_answer(question_type: str, options: List[str], answer: str) -> bool:
    """Validate that the question answer follows the rules"""
    if question_type == "MCQ":
        # MCQ should have exactly one correct answer
        try:
            answer_indices = [int(x.strip()) for x in answer.split(",") if x.strip().isdigit()]
            return len(answer_indices) == 1 and all(0 <= idx < len(options) for idx in answer_indices)
        except:
            return False
    elif question_type == "MSQ":
        # MSQ should have one or more correct answers
        try:
            answer_indices = [int(x.strip()) for x in answer.split(",") if x.strip().isdigit()]
            return len(answer_indices) >= 1 and all(0 <= idx < len(options) for idx in answer_indices)
        except:
            return False
    elif question_type == "NAT":
        # NAT should be a numerical value
        try:
            float(answer)
            return True
        except:
            return False
    elif question_type == "SUB":
        # SUB can be any text
        return len(answer.strip()) > 0
    return False

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
        
        # Get existing questions for reference (but not to copy)
        existing_questions = supabase.table("questions_topic_wise").select("question_statement, options, question_type").eq("topic_id", request.topic_id).limit(5).execute()
        
        # Get previously generated questions to avoid repetition
        generated_questions = supabase.table("new_questions").select("question_statement").eq("topic_id", request.topic_id).limit(10).execute()
        
        # Create prompt for Gemini
        prompt = f"""
You are an expert question creator for educational content. Generate a {request.question_type} type question for the following topic:

Topic: {topic['name']}
Description: {topic.get('description', '')}
Chapter: {chapter.get('name', '')}

Question Type Rules:
- MCQ: Multiple Choice Question with exactly ONE correct answer (4 options)
- MSQ: Multiple Select Question with ONE OR MORE correct answers (4 options)
- NAT: Numerical Answer Type with a numerical answer (no options)
- SUB: Subjective question with descriptive answer (no options)

Context from existing questions (DO NOT COPY, use for inspiration only):
{json.dumps([q['question_statement'] for q in existing_questions.data[:3]], indent=2)}

Previously generated questions (AVOID similar content):
{json.dumps([q['question_statement'] for q in generated_questions.data], indent=2)}

Requirements:
1. Generate a FRESH, ORIGINAL question that tests understanding of the topic
2. Make it educationally valuable and appropriately challenging
3. For MCQ/MSQ: Provide exactly 4 options
4. Ensure the answer follows the question type rules
5. Provide a detailed solution explanation

Please respond in the following JSON format:
{{
    "question_statement": "Your question here",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"] or null for NAT/SUB,
    "answer": "For MCQ: single number (0-3), for MSQ: comma-separated numbers (0,1,2), for NAT: numerical value, for SUB: descriptive answer",
    "solution": "Detailed step-by-step solution",
    "difficulty_level": "Easy/Medium/Hard"
}}
"""

        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response_text[start_idx:end_idx]
            generated_data = json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=500, detail=f"Error parsing AI response: {str(e)}")

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
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Save to database
        result = supabase.table("new_questions").insert(new_question).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error saving question to database")

        return GeneratedQuestion(**new_question)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

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