from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from typing import List

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
    user_answers: List[str]  # List of user-provided answers
    correct_answers: List[str]  # List of correct answers

# 📝 Answer Comparison Prompt Template
comparison_prompt = PromptTemplate(
    input_variables=["user_answer", "correct_answer"],
    template="""
You are an educational evaluator.

Compare the following short answers and determine if the user's answer is sufficiently correct.

User's answer: {user_answer}
Correct answer: {correct_answer}

Consider the following:
- The user's answer might be brief or missing some context.
- If the core meaning or important keywords match, consider it correct.
- If it misses key concepts or changes the meaning, mark it incorrect.
- Judge the answer based on the semantic meaning as user might not write complete sentence.
Return only 'correct' or 'incorrect'.
"""
)

output_parser = StrOutputParser()

# 🚀 Endpoint to compare answers and calculate percentage
@router.post("/compare-answers/")
async def compare_answers(request: AnswerComparisonRequest):
    try:
        correct_count = 0
        wrong_count = 0
        incorrect_answers = []

        for index, correct_answer in enumerate(request.correct_answers):
            try:
                user_answer = request.user_answers[index]
            except IndexError:
                user_answer = ""  # User did not answer this question

            prompt = comparison_prompt.format(
                user_answer=user_answer,
                correct_answer=correct_answer
            )

            raw_output = llm.invoke(prompt)
            result = raw_output.content.strip().lower()

            if result == "correct":
                correct_count += 1
            else:
                wrong_count += 1
                incorrect_answers.append({
                    "question": index + 1,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer
                })

        total_count = len(request.correct_answers)
        percentage = (correct_count / total_count) * 100 if total_count > 0 else 0

        return {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "percentage_correct": round(percentage, 2),
            "incorrect_answers": incorrect_answers
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from typing import List

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
    user_answers: List[str]  # List of user-provided answers
    correct_answers: List[str]  # List of correct answers

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
        correct_count = 0
        wrong_count = 0
        incorrect_answers = []

        for index, correct_answer in enumerate(request.correct_answers):
            try:
                user_answer = request.user_answers[index]
            except IndexError:
                user_answer = ""  # User did not answer this question

            prompt = comparison_prompt.format(
                user_answer=user_answer,
                correct_answer=correct_answer
            )

            raw_output = llm.invoke(prompt)
            result = raw_output.content.strip().lower()

            if result == "correct":
                correct_count += 1
            else:
                wrong_count += 1
                incorrect_answers.append({
                    "question": index + 1,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer
                })

        total_count = len(request.correct_answers)
        percentage = (correct_count / total_count) * 100 if total_count > 0 else 0

        return {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "percentage_correct": round(percentage, 2),
            "incorrect_answers": incorrect_answers
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

