import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.MCQ_GEN.utils import read_file, get_table_data
from src.MCQ_GEN.logger import logging

from langchain.chat_momdels import chatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

