# import os
# import json
# import PyPDF2
# import traceback

# def read_file(file):
#     if file.name.endswith(".pdf"):
#         try:
#             pdf_reader = PyPDF2.PdfFileReader(file)
#             text = " "
#             for page in pdf_reader.pages:
#                 text += page.extract_text()
            
#             return text
        
#         except Exception as e:
#             raise Exception(f"Error while reading the PDF File!")
    
#     elif file.name.endswith(".txt"):
#         return file.read().decode("utf-8")

#     else:
#         raise Exception(
#             f"Unsupported file format only pdf and text file supported"
#         )
    
# def get_table_data(quiz_str):
#     try:
#         quiz_dict = json.loads(quiz_str)
#         quiz_table_data = []

#         for key, value in quiz_dict.items():
#             mcq = value["MCQ"]
#             options = " || ".join(
#                 [
#                     f"{option} -> {option_value}" for option, option_value in value["Options"].items()
#                 ]
#             )

#             correct = value["Correct Answer"]
#             quiz_table_data.append({"MCQ" : mcq, "Choices": options, "Correct Answer": correct})
        
#         return quiz_table_data
    
#     except Exception as e:
#         traceback.print_exception(type(e), e, e.__traceback__)
#         return False

import os
import json
import traceback
from PyPDF2 import PdfReader
import re

def read_file(file):
    """
    Reads the uploaded file (PDF or TXT) and returns the extracted text.
    Raises an exception for unsupported formats or reading errors.
    """
    if file.name.endswith(".pdf"):
        try:
            file.seek(0)  # Reset file pointer for Streamlit uploads
            pdf_reader = PdfReader(file)
            text = ""

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

            return text

        except Exception as e:
            raise Exception(f"Error while reading the PDF file: {str(e)}")

    elif file.name.endswith(".txt"):
        try:
            return file.read().decode("utf-8")
        except Exception as e:
            raise Exception(f"Error while reading the TXT file: {str(e)}")

    else:
        raise Exception("Unsupported file format. Only PDF and TXT files are supported.")


import json
import traceback
import re

import json
import traceback
import re

import json
import traceback
import re

def get_table_data(quiz_str):
    """
    Converts a JSON-like string from GPT output into a structured table.
    Handles markdown code blocks, stray text, and invalid escapes.
    """
    try:
        if not quiz_str or not isinstance(quiz_str, str):
            raise ValueError("Empty or non-string quiz content received.")

        # 1. Try to extract from ```json ... ``` block
        match = re.search(r"```json\s*(\{.*\})\s*```", quiz_str, re.DOTALL)
        if match:
            quiz_str = match.group(1).strip()
        else:
            # 2. Fallback: extract the first {...} block
            brace_match = re.search(r"(\{.*\})", quiz_str, re.DOTALL)
            if brace_match:
                quiz_str = brace_match.group(1).strip()
            else:
                raise ValueError("Quiz string does not contain any JSON block.")

        # 3. Sanitize invalid escape sequences
        quiz_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', quiz_str)

        # 4. Parse JSON
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        for key, value in quiz_dict.items():
            mcq = value.get("MCQ", "N/A")
            options_dict = value.get("Options", {})
            correct = value.get("Correct Answer", "N/A")

            options = " || ".join(
                f"{option} -> {option_value}" for option, option_value in options_dict.items()
            )

            quiz_table_data.append({
                "MCQ": mcq,
                "Choices": options,
                "Correct Answer": correct
            })

        return quiz_table_data

    except Exception as e:
        print("❌ Failed to parse quiz_str as JSON.\n\nRaw string:\n", quiz_str)
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

