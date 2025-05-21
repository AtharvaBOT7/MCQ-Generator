import os
import json
from dotenv import load_dotenv
import traceback
from datetime import datetime
from src.MCQGenerator.logger import logging
from src.MCQGenerator.utils import read_file, get_table_data

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# Initialize ChatOpenAI LLM
llm = ChatOpenAI(openai_api_key=key, model="gpt-4o", temperature=0.5)

# Prompt template for quiz generation
TEMPLATE = """ 
Text: {text}

You are an expert MCQ Generator. Given the above text, your task is to generate a quiz of {number} multiple choice questions in a {tone} tone for the subject {subject}.

These multiple choice questions will be used by a professor to assess students, so ensure that they are:
- non-repetitive,
- relevant to the input text,
- challenging enough for academic evaluation,
- and aligned with the cognitive level of the students.

You must strictly follow the RESPONSE_JSON format provided below and only return the JSON object.

### RESPONSE_JSON
{response_json}

⚠️ Important Instructions:
- ❌ DO NOT include explanations, notes, or introductory text.
- ❌ DO NOT wrap the response in markdown formatting like ```json ... ```.
- ✅ ONLY return a single, valid JSON object that matches the structure exactly.
- ✅ Ensure all keys, braces, and quotes are properly closed and escaped.

Begin your response now:
"""


quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE
)

# Prompt template for quiz review
TEMPLATE2 = """ 
You are an expert English evaluator. You will check the quiz questions for grammar and spelling mistakes. 
You will be given multiple choice questions for {subject} students.
Your task is to evaluate the complexity of the questions and give a complete analysis of the quiz. Use a maximum of 50 words for the analysis. 
If the quiz is not aligned with the cognitive and analytical ability of the students, then we must regenerate the questions to better fit the students' needs.

Quiz_MCQ:
{quiz}
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=TEMPLATE2
)

# Create individual pipelines
quiz_chain = quiz_generation_prompt | llm
review_chain = quiz_evaluation_prompt | llm

# Define a runnable function that simulates SequentialChain
def generate_evaluate_chain_fn(inputs):
    try:
        # Step 1: Generate quiz
        quiz = quiz_chain.invoke(inputs)
        
        # Step 2: Evaluate quiz
        inputs_with_quiz = {**inputs, "quiz": quiz}
        review = review_chain.invoke(inputs_with_quiz)

        return {
            "quiz": quiz,
            "review": review
        }
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return {"quiz": None, "review": "Error occurred during quiz generation."}

# Runnable for use in Streamlit or other scripts
generate_evaluate_chain = RunnableLambda(generate_evaluate_chain_fn)
