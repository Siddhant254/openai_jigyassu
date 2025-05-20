from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.vector_store import retrieve_from_vector_db
from dotenv import load_dotenv
import os 

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

# 🔐 LLM setup
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=openai_api_key
)
output_parser = StrOutputParser()

# 📥 Input model
class FlashcardRequest(BaseModel):
    subject: str
    student_class: str
    topic: str
    difficulty: str  # "easy", "medium", "hard"

# 🚀 Flashcard Endpoint
@router.post("/generate-flashcard")
async def generate_flashcard(request: FlashcardRequest):
    try:
        # Step 1: Retrieve context from vector DB
        query = f"{request.subject} class {request.student_class} - {request.topic}"
        context = retrieve_from_vector_db(query)

        if not context:
            raise HTTPException(status_code=404, detail="No relevant study material found.")

        # Step 2: Prompt for short-answer flashcard
        prompt = PromptTemplate(
            input_variables=["context", "subject", "student_class", "topic", "difficulty"],
            template="""
You are an expert educator designing flashcards for {subject}, class {student_class}.

Create ONE flashcard question from the topic "{topic}" at a {difficulty} level that should be answered in **only one word or one sentence**, using ONLY the content below.

Do NOT include the answer or explanation.

Context:
{context}
"""
        )

        # Step 3: Run the LLM chain
        chain = prompt | llm | output_parser
        flashcard = chain.invoke({
            "context": context,
            "subject": request.subject,
            "student_class": request.student_class,
            "topic": request.topic,
            "difficulty": request.difficulty
        })

        return {
            "type": "short",
            "flashcard": flashcard.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
