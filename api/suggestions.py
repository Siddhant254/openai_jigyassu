from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, openai_api_key=openai_api_key)

# ✅ Define the input model with code and problem statement
class CodeInput(BaseModel):
    code: str
    problem_statement: str  # Added problem statement

@router.post("/suggest-code/")
async def suggest_code(input: CodeInput):
    try:
        # Updated prompt to include problem statement and code for analysis
        prompt = PromptTemplate(
            input_variables=["code", "problem_statement"],
            template="""
You are a senior developer.

Analyze the following problem statement and the code written by the user, and provide suggestions for improvement.

Problem Statement:
{problem_statement}

Code:
{code}

- Identify any issues or improvements in the code.
- Suggest next steps based on the problem statement and the code.
- Provide 2 different suggestions for the code.
- only 2 suggestions should be generated at maximum.

Return only your suggestions, formatted as separate paragraphs.
"""
        )

        # Initialize output parser to capture suggestions
        output_parser = StrOutputParser()

        # Create the chain for processing the prompt and invoking the LLM
        chain = prompt | llm | output_parser

        # Invoke the chain with the provided code and problem statement
        suggestions = chain.invoke({"code": input.code, "problem_statement": input.problem_statement})

        # Return the suggestions as a list, split by paragraphs
        return {"suggestions": suggestions.strip().split("\n\n")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
