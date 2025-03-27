import os
import json
import logging
import datetime
import traceback
from typing import List
import streamlit as st
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agents import Agent, Runner
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer
import asyncio
import nest_asyncio
from urllib.parse import urlparse

nest_asyncio.apply()

load_dotenv()

# logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"quiz_generator_agents_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# base directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_TEXT_DIR = os.path.join(BASE_DIR, "raw_pdf_text")
SUMMARY_TEXT_DIR = os.path.join(BASE_DIR, "summarized_pdf_text")
JSON_OUTPUT_DIR = os.path.join(BASE_DIR, "json_question_answers")

for directory in [RAW_TEXT_DIR, SUMMARY_TEXT_DIR, JSON_OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# pydantic models for structured output
class Answer(BaseModel):
    text: str = Field(..., description="the text of the answer option")
    score: int = Field(..., description="the score for this answer (5=correct, 2=partially correct, 0=wrong, -2=very wrong)")

class Question(BaseModel):
    theme: str = Field(..., description="the theme this question belongs to")
    question_text: str = Field(..., description="the question text")
    answers: List[Answer] = Field(
        ..., 
        description="list of 4 possible answers",
    )

class Quiz(BaseModel):
    questions: List[Question] = Field(
        ..., 
        description="list of quiz questions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "theme": "example theme",
                        "question_text": "example question?",
                        "answers": [
                            {"text": "correct answer", "score": 5},
                            {"text": "partially correct answer", "score": 2},
                            {"text": "wrong answer", "score": 0},
                            {"text": "very wrong answer", "score": -2}
                        ]
                    }
                ]
            }
        }

def extract_text_from_pdf(pdf_path: str) -> str:
    """extract text from pdf
    Args:
        pdf_path (str): the path of the pdf file to extract text from

    Returns:
        str: the text extracted from the pdf
    """
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        return "\n".join([page.page_content for page in pages])
    except Exception as e:
        logging.error(f"error extracting text from pdf: {str(e)}")
        return ""

def save_text_to_file(text: str, file_path: str) -> None:
    """save text to file
    Args:
        text (str): the text to save
        file_path (str): the path of the file where to save the text
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logging.error(f"error saving text to file: {str(e)}")

def extract_text_from_url(url: str) -> str:
    """extract text from url
    Args:
        url (str): the url to extract text from

    Returns:
        str: the text extracted from the url
    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        # html to text
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        
        # combine pages into a single text
        return "\n".join([doc.page_content for doc in docs_transformed])
    except Exception as e:
        logging.error(f"error extracting text from url {url}: {str(e)}")
        return ""

def get_filename_from_url(url: str) -> str:
    """extract filename from url
    Args:
        url (str): the url to extract filename from

    Returns:
        str: the filename extracted from the url
    """
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or parsed.netloc
    # remove file extension
    filename = os.path.splitext(filename)[0]
    return filename

async def create_quiz_from_text(text: str, model: str, filename: str, language: str):
    """process a single text document through the agent pipeline
    Args:
        text (str): the text to process
        model (str): the openai model to use
        filename (str): the name of the file to process
        language (str): the language to generate the quiz in

    Returns:
        tuple: a tuple containing the quiz and the filename
    """
    try:
        # remove .pdf extension from filename
        base_filename = filename.replace('.pdf', '')
        st.write(f"processing {filename}...")
        
        # processing with summarizer agent
        summarizer = Agent(
            name="text summarizer",
            instructions=f"""
            you are an expert at creating detailed summaries of text.
            create a comprehensive summary that capture all important information.
            all summaries must be in {language}.
            maintain the original meaning while making the content more concise.
            """,
            model=model
        )
        summary_result = await Runner.run(summarizer, text)
        
        # save summary
        summary_path = os.path.join(SUMMARY_TEXT_DIR, f"{base_filename}_summary.txt")
        save_text_to_file(summary_result.final_output, summary_path)
        st.info(f"summary saved in: {summary_path}")
        
        # quiz generation
        quiz_generator = Agent(
            name="quiz generator",
            instructions=f"""
            you are an expert at creating educational quizzes.
            create exactly 10 multiple choice questions based on the provided text.
            
            for each question:
            1. identify a specific theme from the text
            2. create a clear question about that theme
            3. provide exactly 4 answers with these scores:
               - one correct answer (5 points)
               - one partially correct answer, it must be similar to the correct answer but with some details that make them slightly wrong (2 points)
               - one wrong answer (0 points)
               - one wrong and potentially harmful answer (-2 points)
            
            assign these values also according to your knowledge on the argument.
            all questions and answers must be in {language}.
            do not make silly questions.
            make sure each question has exactly 4 answers.
            """,
            output_type=Quiz,
            model="gpt-4o"
        )
        quiz_result = await Runner.run(quiz_generator, summary_result.final_output)
        
        return quiz_result.final_output_as(Quiz), base_filename  
        
    except Exception as e:
        logging.error(f"error processing {filename}: {str(e)}")
        logging.error(traceback.format_exc())
        st.error(f"error processing {filename}: {str(e)}")
        return None, None

def main():
    st.title("Quiz Generator")
    
    st.write("""
    Instructions:
    1. Upload PDF files or enter a list of URLs to generate quizzes from
    2. Files are analyzed and summarized
    3. Quizzes are generated in JSON format
    """)
    
    st.write("---")
    
    # create tabs for pdf and url input
    tab1, tab2 = st.tabs(["PDF files", "URLs"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "upload pdf files", 
            type="pdf", 
            accept_multiple_files=True,
            help="you can upload multiple pdf files. they will be processed one at a time."
        )
    
    with tab2:
        urls = st.text_area(
            "enter urls (one per line)",
            help="enter multiple urls, one per line. they will be processed one at a time."
        )
        urls_list = [url.strip() for url in urls.split('\n') if url.strip()]
        
    st.write("---")
    
    # model selection
    model = st.selectbox(
        "Select model:",
        ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        index=1  # default gpt-4o-mini
    )
    
    # language selection
    language = st.selectbox(
        "Select quiz language:",
        ["English", "Italian", "Spanish", "French", "German", "Portuguese", "Russian", "Chinese", "Japanese", "Korean"],
        index=0  # default English
    )
    
    st.write("---")
    
    # verify api key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("set OPENAI_API_KEY")
        return
    
    if st.button("Generate Quiz"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # process pdfs if present
            if uploaded_files:
                total_files = len(uploaded_files)
                for file_index, pdf_file in enumerate(uploaded_files):
                    status_text.text(f"processing pdf {file_index+1} of {total_files}: {pdf_file.name}")
                    progress_bar.progress(file_index / total_files)
                    
                    # temporary save of uploaded file
                    temp_path = f"temp_{pdf_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(pdf_file.getbuffer())
                    
                    try:
                        # extract text from pdf
                        pdf_text = extract_text_from_pdf(temp_path)
                        if not pdf_text:
                            st.error(f"impossible to extract text from {pdf_file.name}")
                            continue
                        
                        # save raw text
                        base_filename = pdf_file.name.replace('.pdf', '')
                        raw_text_path = os.path.join(RAW_TEXT_DIR, f"{base_filename}.txt")
                        save_text_to_file(pdf_text, raw_text_path)
                        
                        # process text with agents
                        quiz, base_filename = loop.run_until_complete(
                            create_quiz_from_text(pdf_text, model, pdf_file.name, language)
                        )
                        
                        if quiz:
                            # save quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # display quiz in streamlit
                            st.write(f"### quiz for {base_filename}")
                            for question_index, question in enumerate(quiz.questions, 1):
                                st.write(f"\n**question {question_index}:** {question.question_text}")
                                for answer in question.answers:
                                    st.write(f"- ({answer.score} points) {answer.text}")
                            
                            st.write("---")
                    
                    finally:
                        # cleanup temporary file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            
            # process urls if present
            if urls_list:
                total_urls = len(urls_list)
                for url_index, url in enumerate(urls_list):
                    status_text.text(f"processing url {url_index+1} of {total_urls}: {url}")
                    progress_bar.progress(url_index / total_urls)
                    
                    try:
                        # extract text from url
                        url_text = extract_text_from_url(url)
                        if not url_text:
                            st.error(f"impossible to extract text from {url}")
                            continue
                        
                        # extract filename from url
                        base_filename = get_filename_from_url(url)
                        
                        # save raw text
                        raw_text_path = os.path.join(RAW_TEXT_DIR, f"{base_filename}.txt")
                        save_text_to_file(url_text, raw_text_path)
                        
                        # process text with agents
                        quiz, base_filename = loop.run_until_complete(
                            create_quiz_from_text(url_text, model, base_filename, language)
                        )
                        
                        if quiz:
                            # save quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # display quiz
                            st.write(f"### quiz for {url}")
                            for question_index, question in enumerate(quiz.questions, 1):
                                st.write(f"\n**question {question_index}:** {question.question_text}")
                                for answer in question.answers:
                                    st.write(f"- ({answer.score} points) {answer.text}")
                            
                            st.write("---")
                    
                    except Exception as e:
                        st.error(f"error processing url {url}: {str(e)}")
                        logging.error(f"error processing url {url}: {str(e)}")
                        logging.error(traceback.format_exc())
            
            status_text.text("processing completed!")
            progress_bar.progress(1.0)
            
        except Exception as e:
            st.error(f"an error occurred: {str(e)}")
            logging.error(f"error in main processing loop: {str(e)}")
            logging.error(traceback.format_exc())
        
        finally:
            # close event loop
            loop.close()
        
        st.success("all files have been processed!")

if __name__ == "__main__":
    main() 