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


def get_table_data(quiz_str):
    """
    Converts a JSON-like string from GPT output into a structured table.
    Handles markdown wrapping, escape errors, truncation, and extra text.
    """
    try:
        if not quiz_str or not isinstance(quiz_str, str):
            raise ValueError("Empty or non-string quiz content received.")

        # Extract JSON block
        match = re.search(r"```json\s*(\{.*?\})\s*```", quiz_str, re.DOTALL)
        if match:
            quiz_str = match.group(1).strip()
        else:
            brace_match = re.search(r"(\{.*)", quiz_str, re.DOTALL)  # Match from first {
            if brace_match:
                quiz_str = brace_match.group(1).strip()
            else:
                raise ValueError("No JSON block found in response.")

        # Sanitize invalid escapes
        quiz_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', quiz_str)

        # Attempt to balance curly braces if cut-off happened
        open_braces = quiz_str.count('{')
        close_braces = quiz_str.count('}')
        if open_braces > close_braces:
            quiz_str += '}' * (open_braces - close_braces)

        # Parse only first JSON object
        decoder = json.JSONDecoder()
        quiz_dict, _ = decoder.raw_decode(quiz_str)

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