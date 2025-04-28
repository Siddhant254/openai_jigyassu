from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

# 🧠 ChatOpenAI Setup
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,  # Keep temperature 0 for evaluation tasks
    openai_api_key=openai_api_key
)

# 📥 Request model for answer comparison
class AnswerComparisonRequest(BaseModel):
    user_answers: list[str]
    correct_answers: list[str]

# 📝 Answer Comparison Prompt Template
comparison_prompt = PromptTemplate(
    input_variables=["user_answer", "correct_answer"],
    template="""
You are an educational expert. Compare the user's answer with the correct answer.

User's answer: {user_answer}
Correct answer: {correct_answer}

Respond only with 'correct' if user's answer is sufficiently accurate, or 'incorrect' if it is not.
No explanation. Only respond with one word: correct or incorrect.
"""
)

output_parser = StrOutputParser()

# Create a chain
comparison_chain = comparison_prompt | llm | output_parser

# 🚀 Endpoint to compare multiple answers
@router.post("/compare-answers/")
async def compare_answers(request: AnswerComparisonRequest):
    try:
        if len(request.user_answers) != len(request.correct_answers):
            raise HTTPException(status_code=400, detail="Number of user and correct answers do not match.")

        correct_count = 0
        wrong_count = 0
        detailed_results = []

        for user_answer, correct_answer in zip(request.user_answers, request.correct_answers):
            # Chain invocation
            result = comparison_chain.invoke({
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })

            result = result.strip().lower()

            if result == "correct":
                correct_count += 1
                detailed_results.append("correct")
            else:
                wrong_count += 1
                detailed_results.append("incorrect")

        total_questions = len(request.correct_answers)
        percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        return {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "percentage_correct": round(percentage, 2),
            "detailed_results": detailed_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
