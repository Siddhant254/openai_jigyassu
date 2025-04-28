from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.vector_store import retrieve_from_vector_db
import re

from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


router = APIRouter()

# 🧠 LLM setup
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    openai_api_key= openai_api_key
)

# 📥 Request model
class QARequest(BaseModel):
    subject: str
    chapter_name: str

# 📝 Updated Prompt Template
prompt = PromptTemplate(
    input_variables=["context", "subject", "chapter_name"],
    template=""" 
You are an expert educational content generator for the subject: {subject}.

Using ONLY the content provided below, generate exactly 10 questions from the chapter "{chapter_name}" in the following format:

- 4 Multiple Choice Questions along with 4 options  
- 2 Short Answer Questions  
- 4 Fill in the Blanks  

⚠️ For each Multiple Choice Question:
- Provide a clear question
- Provide exactly **4 options** labeled **A**, **B**, **C**, and **D**
- Do NOT include the correct answer

⚠️ Do NOT include explanations. Use only the study material below.

📌 Format strictly like this:

1. MCQ: What is the capital of France?  
A. London  
B. Berlin  
C. Paris  
D. Madrid

2. MCQ: What natural phenomenon did Tilly witness in Thailand that reminded her of the video she saw in class?
A. Tornadoes forming
B. Sea rising and forming whirlpools
C. Snowstorm approaching
D. Earthquake shaking the ground


5. Short Answer: ...  
...  

9. Fill in the Blank: The Earth revolves around the ______.

Do not include the answers for the generated questions in your response.

If the study material is irrelevant to the chapter, respond ONLY with: "Nothing found."

Study Material:
{context}
"""
)

output_parser = StrOutputParser()
qa_chain = prompt | llm | output_parser

# 🚀 Endpoint
@router.post("/generate-qa/")
async def generate_qa(request: QARequest):
    try:
        query = f"{request.subject} - {request.chapter_name}"
        context = retrieve_from_vector_db(query)

        if not context:
            raise HTTPException(status_code=404, detail="No relevant study material found.")

        raw_output = qa_chain.invoke({
            "context": context,
            "subject": request.subject,
            "chapter_name": request.chapter_name
        })

        if "nothing found" in raw_output.lower():
            return {"questions": "Nothing found."}

        # Initialize question categories
        questions = {
            "mcq": [],
            "short_answer": [],
            "fill_in_the_blank": [],
        }

        # Use regex to find MCQ questions and their options
        mcq_pattern = r"(\d+\.\s*MCQ:.*?)(?=\d+\.\s*(?:MCQ|Short Answer|Fill in the Blank)|$)"
        mcq_matches = re.finditer(mcq_pattern, raw_output, re.DOTALL)
        
        for match in mcq_matches:
            mcq_text = match.group(1).strip()
            # Extract question and options
            mcq_parts = mcq_text.split('\n')
            if len(mcq_parts) >= 5:  # Question + 4 options
                question = re.sub(r"^\d+\.\s*MCQ:\s*", "", mcq_parts[0]).strip()
                options = [opt.strip() for opt in mcq_parts[1:5] if opt.strip()]
                
                if len(options) == 4:
                    questions["mcq"].append({
                        "question": question,
                        "options": options
                    })

        # Extract Short Answer questions
        short_answer_pattern = r"\d+\.\s*Short Answer:\s*(.*?)(?=\d+\.\s*(?:MCQ|Short Answer|Fill in the Blank)|$)"
        short_answers = re.finditer(short_answer_pattern, raw_output, re.DOTALL)
        
        for match in short_answers:
            question = match.group(1).strip()
            questions["short_answer"].append(question)

        # Extract Fill in the Blank questions
        fill_blank_pattern = r"\d+\.\s*Fill in the Blank:\s*(.*?)(?=\d+\.\s*(?:MCQ|Short Answer|Fill in the Blank)|$)"
        fill_blanks = re.finditer(fill_blank_pattern, raw_output, re.DOTALL)
        
        for match in fill_blanks:
            question = match.group(1).strip()
            questions["fill_in_the_blank"].append(question)

        # If we didn't find any questions, try an alternative approach
        if not any(questions.values()):
            # Split by numbered items and process line by line
            lines = raw_output.split('\n')
            current_type = None
            current_mcq = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for new question
                if re.match(r'^\d+\.', line):
                    # Save previous MCQ if exists
                    if current_mcq and len(current_mcq["options"]) > 0:
                        questions["mcq"].append(current_mcq)
                        current_mcq = None
                    
                    # Determine question type
                    if "MCQ:" in line:
                        current_type = "mcq"
                        question = re.sub(r'^\d+\.\s*MCQ:\s*', '', line).strip()
                        current_mcq = {"question": question, "options": []}
                    elif "Short Answer:" in line:
                        current_type = "short_answer"
                        question = re.sub(r'^\d+\.\s*Short Answer:\s*', '', line).strip()
                        questions["short_answer"].append(question)
                    elif "Fill in the Blank:" in line:
                        current_type = "fill_in_the_blank"
                        question = re.sub(r'^\d+\.\s*Fill in the Blank:\s*', '', line).strip()
                        questions["fill_in_the_blank"].append(question)
                
                # Process options for MCQ
                elif current_type == "mcq" and current_mcq and re.match(r'^[A-D]\.', line):
                    current_mcq["options"].append(line.strip())
                    # If we have 4 options, save this MCQ
                    if len(current_mcq["options"]) == 4:
                        questions["mcq"].append(current_mcq)
                        current_mcq = None

            # Add the last MCQ if it exists and wasn't added
            if current_mcq and len(current_mcq["options"]) > 0:
                questions["mcq"].append(current_mcq)

        return questions if any(questions.values()) else {"questions": "Nothing found."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))