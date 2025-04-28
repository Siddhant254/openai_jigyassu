from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.vector_store import retrieve_from_vector_db
from random import choice
from dotenv import load_dotenv
import os 

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


router = APIRouter()

# 🔐 LLM setup
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key= openai_api_key
)
output_parser = StrOutputParser()

# 📥 Input model
class FlashcardRequest(BaseModel):
    subject: str
    student_class: str
    topic: str
    difficulty: str  # "easy", "medium", "hard"

# 🚀 Flashcard Endpoint
@router.post("/generate-flashcard/")
async def generate_flashcard(request: FlashcardRequest):
    try:
        # Step 1: Retrieve context from vector DB
        query = f"{request.subject} class {request.student_class} - {request.topic}"
        context = retrieve_from_vector_db(query)

        if not context:
            raise HTTPException(status_code=404, detail="No relevant study material found.")

        # Step 2: Randomly choose flashcard type
        flashcard_type = choice(["mcq", "short"])

        # Step 3: Prompt setup based on type
        if flashcard_type == "mcq":
            prompt = PromptTemplate(
                input_variables=["context", "subject", "student_class", "topic", "difficulty"],
                template="""
You are an expert educator designing flashcards for {subject}, class {student_class}.

Create ONE multiple choice question (MCQ) from the topic "{topic}" at a {difficulty} level using ONLY the content below.

Do NOT include the answer or explanation.

Format:
Question
A. Option A
B. Option B
C. Option C
D. Option D

Context:
{context}
"""
            )
        else:  # short answer
            prompt = PromptTemplate(
                input_variables=["context", "subject", "student_class", "topic", "difficulty"],
                template="""
You are an expert educator designing flashcards for {subject}, class {student_class}.

Create ONE question from the topic "{topic}" at a {difficulty} level that can be answered in a **single word or phrase**, using ONLY the content below.

Do NOT include the answer.

Context:
{context}
"""
            )

        # Step 4: Chain it and invoke
        chain = prompt | llm | output_parser
        flashcard = chain.invoke({
            "context": context,
            "subject": request.subject,
            "student_class": request.student_class,
            "topic": request.topic,
            "difficulty": request.difficulty
        })

        return {
            "type": flashcard_type,
            "flashcard": flashcard.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
