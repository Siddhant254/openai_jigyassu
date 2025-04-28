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
    temperature=0.7,
    openai_api_key=openai_api_key
)

# 📥 Request model for answer comparison
class AnswerComparisonRequest(BaseModel):
    user_answers: list[str]  # List of user-provided answers
    correct_answers: list[str]  # List of correct answers

# 📝 Answer Comparison Prompt Template
comparison_prompt = PromptTemplate(
    input_variables=["user_answer", "correct_answer"],
    template="""
You are an educational expert. You will compare the user's answer with the correct answer.

Here is the user's answer: {user_answer}
Here is the correct answer: {correct_answer}

Determine if the user's answer is correct or incorrect. Provide 'correct' if the answer is sufficiently accurate and 'incorrect' if it is not. Do not provide explanations, just return 'correct' or 'incorrect'.
"""
)

output_parser = StrOutputParser()

# 🚀 Endpoint to compare answers and calculate percentage
@router.post("/compare-answers/")
async def compare_answers(request: AnswerComparisonRequest):
    try:
        if len(request.user_answers) != len(request.correct_answers):
            raise HTTPException(status_code=400, detail="Number of answers do not match.")

        correct_count = 0
        wrong_count = 0

        # Compare the user answers with the correct answers using ChatOpenAI
        for user_answer, correct_answer in zip(request.user_answers, request.correct_answers):
            # Prepare the prompt with the user and correct answer
            prompt = comparison_prompt.format(user_answer=user_answer, correct_answer=correct_answer)

            # Get the response from the LLM
            raw_output = llm(prompt)
            result = raw_output.strip().lower()

            # Check if the answer is 'correct' or 'incorrect'
            if result == "correct":
                correct_count += 1
            else:
                wrong_count += 1

        total_count = len(request.correct_answers)
        percentage = (correct_count / total_count) * 100 if total_count > 0 else 0

        return {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "percentage_correct": round(percentage, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
