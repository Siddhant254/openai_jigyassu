from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")


router = APIRouter()

llm = ChatOpenAI(model=model, temperature=0.0, openai_api_key= openai_api_key)

class ValidationInput(BaseModel):
    problem_statement: str
    code: str

@router.post("/submit")
async def validate_solution(input: ValidationInput):
    try:
        prompt = PromptTemplate(
            input_variables=["problem", "code"],
            template=
            """
            You are an expert programming evaluator.

Your task is to determine whether the following user-submitted code correctly solves the given problem.

### Problem Statement:
{problem}

### User's Code:
{code}

### Evaluation Instructions:
1. First, analyze the problem carefully and understand what the code is expected to do.
2. Run the code mentally or simulate its execution using appropriate test cases based on the problem.
3. Identify any syntax errors, Exceptions, logical errors, missing function calls, or edge case issues.
4. Evaluate the correctness of the approach, completeness of the logic, and code quality.

### Your Response Should Include:
- One of the following verdicts:
  - **Correct Solution**
  - **Incorrect solution**
- A brief explanation for your verdict.
- If incorrect, clearly mention what the code is doing wrong.
- Suggest areas of improvement (e.g., syntax, logic, edge cases, code structure).
- Mention the programming concepts or topics involved in the solution (e.g., loops, recursion, string manipulation, etc.).
- Ignore the upper case/lower case conventions for verdicts.

Be honest, concise, and constructive in your feedback.
            """ )
        
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        result = chain.invoke({
            "problem": input.problem_statement,
            "code": input.code})

        return {"result": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
