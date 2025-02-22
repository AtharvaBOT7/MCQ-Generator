from setuptools import setup, find_packages

setup(
    name='MCQ_GEN',
    version='0.1',
    author = 'Atharva Chundurwar',
    author_email = 'atharvachundurwar841@gmail.com',
    install_requires=["openai","langchain","streamlit","python-dotenv","PyPDF2"],
    packages=find_packages()
)