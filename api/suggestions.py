from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

router = APIRouter()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, openai_api_key="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")

class CodeInput(BaseModel):
    code: str

@router.post("/suggest-code/")
async def suggest_code(input: CodeInput):
    try:
        prompt = PromptTemplate(
            input_variables=["code"],
            template="""
You are a senior developer.

Analyze the following code and provide suggestions .

- Identify any improvements or potential issues.
- Suggest next steps in the current code and provide the corrected code.
- Generate 2 different suggestions.

Code:
{code}

Return only your suggestions.
"""
        )

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        suggestions = chain.invoke({"code": input.code})

        return {"suggestions": suggestions.strip().split("\n\n")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
