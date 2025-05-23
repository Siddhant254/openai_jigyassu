from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.vector_store import retrieve_from_vector_db
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

router = APIRouter()

# 🧠 LLM setup
llm = ChatOpenAI(
    model=model,
    temperature=0.7,
    openai_api_key=openai_api_key
)

# 📝 Modified Request Model based on new format
class MCQ(BaseModel):
    question: str
    options: list[str]

class QARequest(BaseModel):
    mcq: list[MCQ]  # List of MCQs
    short_answer: list[str]  # List of short answer questions
    fill_in_the_blank: list[str]  # List of fill-in-the-blank questions
    subject: str
    chapter: str
    material_id: str

# 📥 Request model for generating answers
class AnswerRequest(BaseModel):
    context: str
    question: str

# 🧑‍🏫 LLM Prompt Template
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert educational evaluator.

You will answer the following question based on the provided study material. 
If the answer is clear, concise, and based on the context, provide it directly. 
If you are unsure or need to make assumptions, explain them as well.

Context:
{context}

Question:
{question}

Answer:
"""
)

output_parser = StrOutputParser()
qa_chain = prompt | llm | output_parser

# 🚀 Endpoint to answer questions based on study material
@router.post("/answer-questions")
async def answer_questions(request: QARequest):
    try:
        # 1️⃣ Retrieve relevant content from the vector store using subject and chapter name
        context = retrieve_from_vector_db(
            subject=request.subject,
            chapter = request.chapter,
            material_id = request.material_id)

        if not context:
            raise HTTPException(status_code=404, detail="No relevant study material found.")

        # 2️⃣ Generate answers for the provided questions based on the retrieved study material
        answers = []

        # For MCQ questions, we pass the question and options
        for mcq in request.mcq:
            question_with_options = (
    f"Question: {mcq.question}\n"
    f"Options: {', '.join(mcq.options)}\n"
    "Choose the correct answer **exactly from the options provided.**"
)
            raw_output = qa_chain.invoke({
                "context": context,
                "question": question_with_options
            })
            answers.append(raw_output.strip())

        # For Short Answer questions
        for short in request.short_answer:
            raw_output = qa_chain.invoke({
                "context": context,
                "question": f"Short Answer Question: {short}"
            })
            answers.append(raw_output.strip())

        # For Fill in the Blank questions
        for fill in request.fill_in_the_blank:
            raw_output = qa_chain.invoke({
                "context": context,
                "question": (
    f"Fill in the blank: {fill}\n"
    "Return **only** the missing word or phrase, not the full sentence."
)
 })
            answers.append(raw_output.strip())
        print(answers)
        return {
            "questions": request.dict(),
            "answers": answers
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
