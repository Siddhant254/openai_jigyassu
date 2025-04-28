from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

router = APIRouter()

# Initialize your OpenAI model (you can keep using GPT-3.5 or switch to GPT-4)
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0,
    openai_api_key="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"
)

class CodeInput(BaseModel):
    code: str

@router.post("/run-code-openai/")
async def run_code_openai(input: CodeInput):
    try:
        prompt = PromptTemplate(
            input_variables=["code"],
            template="""
                    You are a code execution simulator.

                    Please:
                    1. Detect the programming language used.
                    2. Simulate the actual output or error that would occur if this code was run in an IDE.
                    3. Format the output exactly as if it appeared in a terminal or console.

                    Code:
                    ```python
                    {code}
                    Respond with only the output/error as it would appear. 
                    """ 
                    )
        
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        simulated_output = chain.invoke({"code": input.code})

        return {"output": simulated_output.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        