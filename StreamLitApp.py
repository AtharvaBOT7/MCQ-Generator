import os
import traceback
import json
import pandas as pd
from dotenv import load_dotenv
from src.MCQGenerator.utils import read_file, get_table_data
import streamlit as st
from langchain_community.callbacks.manager import get_openai_callback
from src.MCQGenerator.mcqgenerator import generate_evaluate_chain
from src.MCQGenerator.logger import logging

# Load environment variables (for OPENAI_API_KEY if needed elsewhere)
load_dotenv()

# Load the expected response format from JSON
with open('/Users/atharva7/Downloads/MCQ-Generator/Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Streamlit App Title
st.title("MCQ Generator Application using GPT-4o and Langchain 🚀")

# User input form
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Please upload a PDF or TXT file here...")

    mcq_count = st.number_input(
        "How many MCQs do you want to generate?", min_value=3, max_value=50
    )

    subject = st.text_input(
        "Insert the subject related to the file uploaded above:", max_chars=20
    )

    tone = st.text_input(
        "What should be the complexity of the generated questions:",
        max_chars=20,
        placeholder="Simple"
    )

    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                # Extract text from uploaded file
                text = read_file(uploaded_file)

                # Generate quiz and review
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain.invoke({
                        "text": text,
                        "number": mcq_count,
                        "tone": tone,
                        "subject": subject,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("An error occurred while generating MCQs.")

            else:
                # Log token usage and cost
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: ${cb.total_cost:.6f}")

                # Parse and display the quiz
                if isinstance(response, dict):
                    quiz_msg = response.get("quiz", None)
                    quiz = str(quiz_msg) if quiz_msg else None

                    if quiz:
                        table_data = get_table_data(quiz)
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area(label="Review", value=response.get("review", ""))
                        else:
                            st.error("Unable to parse quiz data.")
                    else:
                        st.error("No quiz was generated.")
                else:
                    st.write(response)
