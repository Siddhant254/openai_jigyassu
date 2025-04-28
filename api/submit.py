from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

router = APIRouter()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, openai_api_key="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")

class ValidationInput(BaseModel):
    problem_statement: str
    code: str

@router.post("/submit/")
async def validate_solution(input: ValidationInput):
    try:
        prompt = PromptTemplate(
            input_variables=["problem", "code"],
            template=
            """
            You are an expert programming evaluator.
            Your task is to determine whether the given code correctly solves the provided problem.

            ### Problem:
            {problem}

            ### User's Code:
            {code}
            Respond with one of the following options:Correct solution or Incorrect solution.
            Also tell the topics and areas of improvement for the user by analyzing the code written by the user.
            """ )
        
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        result = chain.invoke({
            "problem": input.problem_statement,
            "code": input.code})

        return {"result": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        