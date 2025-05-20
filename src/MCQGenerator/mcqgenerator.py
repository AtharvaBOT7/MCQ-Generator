# import os
# import json
# from dotenv import load_dotenv
# import pandas as pd
# import traceback
# import logging
# from datetime import datetime
# from src.MCQGenerator.logger import logging
# from src.MCQGenerator.utils import read_file, get_table_data

# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.chains import SequentialChain

# load_dotenv()

# key = os.getenv("OPENAI_API_KEY")

# llm = ChatOpenAI(openai_api_key=key,model_name="gpt-4o",temperature=0.5)

# TEMPLATE = """ 
# Text: {text}
# You are an expert MCQ Generator. Given the above text, your task is to \
# generate a quiz of {number} multiple choice questions in {tone} tone.
# These mulitple choice questions will be used by the professor to test the students so generate difficult questions.
# You have to make sure that the questions are not repeated and then check if all the questions align with the given text or not.
# You also have to make sure that you format your response as per the RESPONSE_JSON below and use it as a guide to generate the questions.

# ### RESPONSE_JSON
# {response_json}
# """

# quiz_generation_prompt = PromptTemplate(
#     input_variables=["text","number","subject","tone","response_json"],
#     template = TEMPLATE
# )

# quiz_chain = LLMChain(llm = llm, prompt = quiz_generation_prompt, output_key = "quiz", verbose = True)

# TEMPLATE2 = """"
# You are expert english evaluator. You will check the quiz questions for grammar and spelling mistakes. 
# You will be given with mulitple choice questions for {subject} students.
# Your task is to evaluate the complexity of the questions and give a complete analysis of the quiz quiz. Only use a maximum of 50 words for the analysis. 
# If the quiz is not as per the cognitive and analytical abilty of the students, then we must generate new questions such that it perfectly fits the 
# student's abilities.

# Quiz_MCQ:
# {quiz}
# """

# quiz_evaluation_prompt = PromptTemplate(input_variables=["subject","quiz"], template = TEMPLATE2)

# review_chain = LLMChain(llm = llm, prompt = quiz_evaluation_prompt, output_key = "review", verbose = True)

# generate_evaluate_chain = SequentialChain(chains = [quiz_chain, review_chain], input_variables = ["text","number","subject","tone","response_json"],
#                                           output_variables = ["quiz","review"], verbose = True)


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
You are an expert MCQ Generator. Given the above text, your task is to \
generate a quiz of {number} multiple choice questions in {tone} tone.
These multiple choice questions will be used by the professor to test the students, so generate difficult questions.
You have to make sure that the questions are not repeated and that all the questions align with the given text.
You also have to make sure that you format your response as per the RESPONSE_JSON below and use it as a guide to generate the questions.

### RESPONSE_JSON
{response_json}
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
