from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

# ✅ OpenAI LLM setup
llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=openai_api_key)
output_parser = StrOutputParser()

def generate_buggy_code(context: list, language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty"],
        template="""
You are a programming instructor.

Generate a {language} code snippet related to the topic: {context}  
The code should be designed for learners to debug.

Instructions:
- Introduce exactly one {difficulty}-level bug in the code.
- The bug should be realistic and related to the topic (e.g., logic error, wrong variable, off-by-one, etc.).
- The code can be a complete function, a partial block, or a script — but should be runnable.
- Do NOT include any explanations or comments indicating the bug.
- Output only the raw code (no markdown, headings, or extra formatting).

Goal: The code should challenge learners to identify and fix the bug based on their understanding of the topic.
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"context": context, "language": language, "difficulty": difficulty})

# --- New Problem Prompt ---
def generate_new_problem(context: list, language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty", "few_shot_examples"],
        template="""
You are a competitive programming problem setter.

Generate a high-quality coding problem in {language} at a {difficulty} level,
based entirely on the following topic: {context}

When determining the difficulty, consider factors such as:
- Algorithmic complexity required to solve the problem
- Data structures involved (e.g., arrays, trees, graphs, heaps, hash maps)
- Problem type (e.g., sorting, dynamic programming, graph traversal, greedy algorithms)
- Edge cases and constraints (input size, time and memory limits)
- Logical and implementation complexity

Requirements:
- Follow the style of platforms like LeetCode, HackerRank, or HackerEarth.
- Include these sections in the problem statement:

  Title: A concise, descriptive title for the problem.

  Description: A clear and detailed explanation of the problem, including real-world logic,
  relevant constraints, and possible edge cases.

  Input: Specify exactly what input the program will receive.

  Output: Describe the expected output clearly.

  Constraints: Provide meaningful constraints such as input size limits, value ranges, and
  performance expectations.

  Examples: Provide at least two input/output examples in the format:
    Input:
    Output:

Do NOT:
- Use markdown formatting (e.g., **bold**, # headers)
- Include the solution or hints

Ensure the response is formatted exactly like a real competitive programming problem.

Context:
{context}
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({
        "context": context,
        "language": language,
        "difficulty": difficulty
    })

# --- Incomplete Code Prompt ---

def generate_incomplete_code(context: list, language: str, difficulty: str) -> str:

    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty"],
        template="""
You are a programming tutor.

Generate an incomplete code snippet **strictly in {language}**, based on the topic: {context}.  
Do not use any other language.

Instructions:
- The code should be mostly written, but with some **key parts intentionally left out**.
- Leave out logical blocks (e.g., conditionals, loop bodies, function definitions, return statements) depending on the difficulty.
- For medium and hard difficulties, you can leave out multiple non-contiguous parts.
- Do NOT include explanations or formatting or hints or comments.
- Do not include language of the code in the output.
- Output only the raw code, and it must be valid {language} syntax.

Goal: The user should complete the missing parts based on their understanding of the topic.

"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"context": context, "language": language, "difficulty": difficulty})


def generate_fallback_buggy_code(language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["language", "difficulty"],
        template="""
You are a programming instructor.

Generate a {language} code snippet intended for learners to debug.

Instructions:
- Introduce realistic {difficulty}-level bugs in the code.
- The code can include **one or more bugs** (e.g., logic errors, incorrect variables, off-by-one errors, wrong conditions, etc.).
- The code can be a complete function, a partial block, or a script — but should be runnable.
- Do NOT include any explanations or comments indicating the bugs.
- Output only the raw code (no markdown, headings, or extra formatting).

Goal: The code should challenge learners to identify and fix the bugs based on their understanding of programming logic and syntax.
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"language": language, "difficulty": difficulty})



def generate_fallback_new_problem(language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["language", "difficulty"],
        template="""
You are a competitive programming problem setter.

Generate a high-quality coding problem in {language} at a {difficulty} level.  
Use a general programming topic suitable for practice.

📝 Requirements:
- Use a style similar to LeetCode, HackerRank, or HackerEarth.
- The problem must include the following sections:

  Title: A concise title for the problem.

  Description: A clear and structured explanation of the problem statement. Focus on logical conditions and edge cases.

  Input: Explain exactly what inputs will be provided.

  Output: Describe the expected output.

  Constraints: Provide realistic constraints (e.g., value ranges, input size).

  Examples: Include at least 2 input/output examples.  
    Format like:  
    Input: ...  
    Output: ...

❌ Do NOT use markdown formatting  
❌ Do NOT include the solution or explanation  
✅ Keep the output concise and challenge-focused
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"language": language, "difficulty": difficulty})


def generate_fallback_incomplete_code(language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["language", "difficulty"],
        template="""
You are a programming tutor.

Generate an incomplete code snippet in {language}.  
The code should be mostly written, but leave out some **key parts** depending on the {difficulty}.

Instructions:
- Leave out logical blocks (e.g., conditionals, loop bodies, return statements, function bodies).
- For medium and hard difficulties, you may leave out multiple non-contiguous parts.
- Do NOT include any comments, explanations, or formatting.
- Do not mention the language in the output.
- Output only the raw code using valid {language} syntax.

Goal: Challenge learners to complete the missing parts based on logic and syntax.
"""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"language": language, "difficulty": difficulty})
