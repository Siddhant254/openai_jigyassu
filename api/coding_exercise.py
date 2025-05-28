from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.vector_store import retrieve_from_vector_db
from utils.langchain_rag import (
    generate_buggy_code, 
    generate_new_problem, 
    generate_incomplete_code,
    generate_fallback_buggy_code,
    generate_fallback_incomplete_code,
    generate_fallback_new_problem
)

router = APIRouter()

# Define the request model
class CodingRequest(BaseModel):
    language: str
    problem_type: str  # "bug_finding", "new_code", or "missing_code"
    query: str = None
    difficulty: str = "medium"  # default to "medium" if not provided

@router.post("/coding-exercise")
async def coding_exercise(request: CodingRequest):
    try:
        # 1️⃣ Try retrieving content from vector store
        if request.query:
            study_material = retrieve_from_vector_db(request.query)
        else:
            study_material = None

        # 2️⃣ Choose appropriate generation function
        if request.problem_type == "bug_finding":
            code = (generate_buggy_code(study_material, request.language, request.difficulty)
                    if study_material else generate_fallback_buggy_code(request.language, request.difficulty))

        elif request.problem_type == "new_code":
            code = (generate_new_problem(study_material, request.language, request.difficulty)
                    if study_material else generate_fallback_new_problem(request.language, request.difficulty))

        elif request.problem_type == "missing_code":
            code = (generate_incomplete_code(study_material, request.language, request.difficulty)
                    if study_material else generate_fallback_incomplete_code(request.language, request.difficulty))
        
        else:
            raise HTTPException(status_code=400, detail="Invalid problem type")

        print(f"Problem Type: {request.problem_type}, Language: {request.language}, Difficulty: {request.difficulty}, Fallback: {'Yes' if not study_material else 'No'}")

        # 3️⃣ Return the challenge response
        return {
            "language": request.language,
            "problem_type": request.problem_type,
            "difficulty": request.difficulty,
            "challenge": code.strip("`").split("\n", 1)[-1]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
