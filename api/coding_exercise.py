from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.vector_store import retrieve_from_vector_db
from utils.langchain_rag import (
    generate_buggy_code, 
    generate_new_problem, 
    generate_incomplete_code
)

router = APIRouter()

# ✅ Define the request model
class CodingRequest(BaseModel):
    language: str
    problem_type: str  # "bug_finding", "new_code", or "missing_code"
    query: str
    difficulty: str = "medium"  # default to "medium" if not provided

@router.post("/coding-exercise/")
async def coding_exercise(request: CodingRequest):
    try:
        # 1️⃣ Retrieve relevant content from the vector store using RAG
        study_material = retrieve_from_vector_db(request.query)

        if not study_material:
            raise HTTPException(status_code=404, detail="No study material found")

        # 2️⃣ Generate the challenge based on the type
        if request.problem_type == "bug_finding":
            code = generate_buggy_code(study_material, request.language, request.difficulty)
        elif request.problem_type == "new_code":
            code = generate_new_problem(study_material, request.language, request.difficulty)
        elif request.problem_type == "missing_code":
            code = generate_incomplete_code(study_material, request.language, request.difficulty)
        else:
            raise HTTPException(status_code=400, detail="Invalid problem type")

        # 3️⃣ Return the response
        return {
            "language": request.language,
            "problem_type": request.problem_type,
            "difficulty": request.difficulty,
            "challenge": code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
