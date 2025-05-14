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
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=oai_api_key)
output_parser = StrOutputParser()
# --- Buggy Code Prompt ---
def generate_buggy_code(context: list, language: str, difficulty: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "language", "difficulty"],
        template="""
You are a programming instructor.

Generate a {language} code snippet related to the topic: {context}.

Instructions:
- Introduce bugs based on the selected difficulty:
  - easy: 1 simple bug (e.g., typo, wrong operator, off-by-one).
  - medium: 2 subtle bugs (e.g., flawed logic, wrong data type, bad loop condition).
  - hard: 3 or more complex bugs (e.g., edge case failures, incorrect algorithm design, nested logic flaws, misuse of built-in functions).
- The bugs must be realistic and challenge learners to identify and fix them.
- The code can be a complete function, a script, or a code block — but must resemble real-world code.
- Do NOT explain or comment on the bugs.
- Do NOT use markdown or formatting — return plain raw code only.
- Do not give any hints or comments to help a solver.

Your goal: Create code that tests the learner’s understanding of the topic through intentional bugs.

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

Generate a high-quality coding problem in {language} at a {difficulty} level.  
Base the problem entirely on the following topic: {context}

📝 Requirements:
- Use a style similar to LeetCode, HackerRank, or HackerEarth.
- The problem must include the following sections:

  **Title**: A concise title for the problem.

  **Description**: A clear and structured explanation of the problem statement. Focus on real-world logic, constraints, or edge cases.

  **Input**: Explain exactly what inputs will be provided.

  **Output**: Describe the expected output.

  **Constraints**: Provide meaningful constraints (e.g., value ranges, input size, performance expectations).

  **Examples**: Include at least 2 input/output examples.  
    Format like:  
    Input: ...  
    Output: ...

❌ Do NOT use markdown (like `**` or `#`)  
❌ Do NOT include the solution.  
❌ Do NOT include explanation or hints.  
✅ Format the response like a real competitive programming problem.

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
- Do NOT include explanations or formatting or hints.
- Output only the raw code, and it must be valid {language} syntax.

Goal: The user should complete the missing parts based on their understanding of the topic."""
    )
    chain = prompt | llm | output_parser
    return chain.invoke({"context": context, "language": language, "difficulty": difficulty})

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
