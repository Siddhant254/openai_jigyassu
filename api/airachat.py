from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import openai
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

router = APIRouter()

# LLM Setup
llm = ChatOpenAI(
    model = model,
    temperature = 0.7,
    openai_api_key = openai_api_key
)

output_parser = StrOutputParser()

# Data Validation
class AirachatRequest(BaseModel):
    user_query: str

# Openai Moderation 
def is_unsafe(text:str)-> bool:
    try:
        response = openai.Moderation.create(input=text)
        return response["results"][0]["flagged"]
    
    except Exception as e:
        print("Moderation API Error",e)
        return True
    
# Chatbot Endpoint
@router.post("/aira-chat")
async def aira_chat(request: AirachatRequest):
    try:
        if is_unsafe(request.user_query):
            return {"response": "Sorry, I can't respond to that question."}
        
        else:
            prompt = ChatPromptTemplate(
                input_variables = ["question"],
                template = """
You are a knowledgeable assistant. Answer the following question using your general knowledge.

Question: {question}

Answer:"""
)
            chain = llm | prompt | output_parser
            response = chain.invoke({
                "question": request.user_query
            })

            return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail = str(e))










