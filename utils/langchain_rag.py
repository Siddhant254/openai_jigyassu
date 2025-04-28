from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ OpenAI LLM setup
oai_api_key = openai_api_key
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=oai_api_key)
output_parser = StrOutputParser()

# FEW_SHOT_EXAMPLES = """
# === BEGIN ===

# **Title**: Sum of Even Numbers  
# **Description**:  
# Given a positive integer N, compute the sum of all even numbers from 1 to N inclusive.  

# **Input**:  
# A single integer N.  

# **Output**:  
# A single integer representing the sum of even numbers from 1 to N.  

# **Constraints**:  
# 1 ≤ N ≤ 1000  

# **Examples**:  
# Input: 10  
# Output: 30  

# Input: 7  
# Output: 12  

# === END ===

# === BEGIN ===

# **Title**: Count Vowels in a String  
# **Description**:  
# Given a string consisting of lowercase English letters, determine how many vowels it contains.  

# **Input**:  
# A single string of lowercase characters.  

# **Output**:  
# An integer representing the number of vowels in the string.  

# **Constraints**:  
# 1 ≤ Length of string ≤ 100  

# **Examples**:  
# Input: "education"  
# Output: 5  

# Input: "sky"  
# Output: 0  

# === END ===

# === BEGIN ===

# **Title**: Find Maximum in List  
# **Description**:  
# You are given a list of integers. Your task is to return the maximum value from the list.  

# **Input**:  
# A list of integers separated by spaces.  

# **Output**:  
# An integer representing the largest number in the list.  

# **Constraints**:  
# 1 ≤ Number of elements ≤ 100  
# -1000 ≤ Each element ≤ 1000  

# **Examples**:  
# Input: [4, 8, 1, 9]  
# Output: 9  

# Input: [-3, -1, -7]  
# Output: -1  

# === END ===
# """

# --- Buggy Code Prompt ---
def generate_buggy_code(context: list, language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty"],
        template="""
You are a coding instructor.
Generate a single {language} function that intentionally contains a {difficulty}-level bug.
Use only the context below:
{context}

Do not include explanations or formatting. Return only the buggy code.
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"context": context, "language": language, "difficulty": difficulty})

# --- New Problem Prompt ---
def generate_new_problem(context: list, language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty", "few_shot_examples"],
        template="""
-Generate a new coding problem in the {language} programming language at a {difficulty} level.
-Do not provide symbols like (*) in the response
- Do not provide heading called problem statement as we have it already in our frontend.
-Base the problem entirely on the following topic: {context}
- The output response should be properly formatted so that it looks good on frontend app.

All the points mentioned above should be followed in the response


"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({
        "context": context,
        "language": language,
        "difficulty": difficulty
    })

# --- Incomplete Code Prompt ---
MISSING_CODE_EXAMPLES = {
    "easy": "Write a loop to sum even numbers between 1 and N.",
    "medium": "Implement binary search logic.",
    "hard": "Fill missing logic for finding LIS (Longest Increasing Subsequence)."
}

def generate_incomplete_code(context: list, language: str, difficulty: str) -> str:
    example = MISSING_CODE_EXAMPLES.get(difficulty, "Complete a partially written function.")
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty", "example"],
        template="""
You are a coding tutor.
Based on the context: {context}, generate an incomplete {language} function of {difficulty} difficulty.
Add a # TODO where logic is missing and 1-2 hints as comments.
Do not return any explanation.
Example to follow: {example}
Return only the code.
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"context": context, "language": language, "difficulty": difficulty, "example": example})


def generate_qa_pairs(context: str, qa_type: str, difficulty: str):
    prompt = PromptTemplate.from_template("""
    You are an intelligent assistant. Based on the study material below, generate 3 {qa_type} questions and answers.
    Keep them {difficulty} level.

    Study Material:
    {context}

    Format:
    Q1: ...
    A1: ...
    """)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run(qa_type=qa_type, difficulty=difficulty, context=context)
