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

# directory di base 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_TEXT_DIR = os.path.join(BASE_DIR, "raw_pdf_text")
SUMMARY_TEXT_DIR = os.path.join(BASE_DIR, "summarized_pdf_text")
JSON_OUTPUT_DIR = os.path.join(BASE_DIR, "json_question_answers")

for directory in [RAW_TEXT_DIR, SUMMARY_TEXT_DIR, JSON_OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# modelli pydantic per l'output strutturato
class Answer(BaseModel):
    text: str = Field(..., description="il testo dell'opzione di risposta")
    score: int = Field(..., description="il punteggio per questa risposta (5=corretta, 2=parzialmente corretta, 0=sbagliata, -2=molto sbagliata)")

class Question(BaseModel):
    theme: str = Field(..., description="il tema a cui appartiene questa domanda")
    question_text: str = Field(..., description="il testo della domanda")
    answers: List[Answer] = Field(
        ..., 
        description="lista di 4 possibili risposte",
    )

class Quiz(BaseModel):
    questions: List[Question] = Field(
        ..., 
        description="lista delle domande del quiz"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "theme": "esempio tema",
                        "question_text": "esempio domanda?",
                        "answers": [
                            {"text": "risposta corretta", "score": 5},
                            {"text": "risposta parzialmente corretta", "score": 2},
                            {"text": "risposta sbagliata", "score": 0},
                            {"text": "risposta molto sbagliata", "score": -2}
                        ]
                    }
                ]
            }
        }

def extract_text_from_pdf(pdf_path: str) -> str:
    """estrazione del testo dal pdf
    Args:
        pdf_path (str): il percorso del file pdf da cui estrarre il testo

    Returns:
        str: il testo estratto dal pdf
    """
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        return "\n".join([page.page_content for page in pages])
    except Exception as e:
        logging.error(f"errore nell'estrazione del testo dal pdf: {str(e)}")
        return ""

def save_text_to_file(text: str, file_path: str) -> None:
    """salvataggio del testo su file
    Args:
        text (str): il testo da salvare
        file_path (str): il percorso del file dove salvare il testo
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logging.error(f"errore nel salvataggio del testo su file: {str(e)}")

def extract_text_from_url(url: str) -> str:
    """estrazione del testo dall'url
    Args:
        url (str): l'url da cui estrarre il testo

    Returns:
        str: il testo estratto dall'url
    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        # html in testo
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        
        # combino le pagine in un unico testo
        return "\n".join([doc.page_content for doc in docs_transformed])
    except Exception as e:
        logging.error(f"errore nell'estrazione del testo dall'url {url}: {str(e)}")
        return ""

def get_filename_from_url(url: str) -> str:
    """estrazione del nome file dall'url
    Args:
        url (str): l'url da cui estrarre il nome file

    Returns:
        str: il nome file estratto dall'url
    """
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or parsed.netloc
    # rimuovo l'estensione del file
    filename = os.path.splitext(filename)[0]
    return filename

async def create_quiz_from_text(text: str, model: str, filename: str):
    """elaborazione di un singolo documento di testo attraverso la pipeline degli agenti
    Args:
        text (str): il testo da elaborare
        model (str): il modello openai da utilizzare
        filename (str): il nome del file da elaborare

    Returns:
        tuple: una tupla contenente il quiz e il nome del file
    """
    try:
        # rimozione dell'estensione .pdf dal nome file
        base_filename = filename.replace('.pdf', '')
        st.write(f"elaborazione di {filename}...")
        
        # elaborazione con l'agente per il riassunto
        summarizer = Agent(
            name="text summarizer",
            instructions="""
            you are an expert at creating detailed summaries of text.
            create a comprehensive summary that capture all important information.
            all summaries must be in italian.
            maintain the original meaning while making the content more concise.
            """,
            model=model
        )
        summary_result = await Runner.run(summarizer, text)
        
        # salvo il riassunto
        summary_path = os.path.join(SUMMARY_TEXT_DIR, f"{base_filename}_summary.txt")
        save_text_to_file(summary_result.final_output, summary_path)
        st.info(f"riassunto salvato in: {summary_path}")
        
        # generazione del quiz
        quiz_generator = Agent(
            name="quiz generator",
            instructions="""
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
            all questions and answers must be in italian.
            do not make silly questions.
            make sure each question has exactly 4 answers.
            """,
            output_type=Quiz,
            model="gpt-4o"
        )
        quiz_result = await Runner.run(quiz_generator, summary_result.final_output)
        
        return quiz_result.final_output_as(Quiz), base_filename  
        
    except Exception as e:
        logging.error(f"errore nell'elaborazione di {filename}: {str(e)}")
        logging.error(traceback.format_exc())
        st.error(f"errore nell'elaborazione di {filename}: {str(e)}")
        return None, None

def main():
    st.title("Generatore di quiz")
    
    st.write("""
    Istruzioni:
    1. Caricare files PDF o inserire una lista di URL dai quali si intende generare i quiz
    2. I file vengono analizzati e riassunti
    3. Vengono generati i quiz in formato JSON
    """)
    
    st.write("---")
    
    # creazione delle schede per input pdf e url
    tab1, tab2 = st.tabs(["file pdf", "url"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "carica file pdf", 
            type="pdf", 
            accept_multiple_files=True,
            help="puoi caricare più file pdf. verranno elaborati uno alla volta."
        )
    
    with tab2:
        urls = st.text_area(
            "inserisci gli url (uno per riga)",
            help="inserisci più url, uno per riga. verranno elaborati uno alla volta."
        )
        urls_list = [url.strip() for url in urls.split('\n') if url.strip()]
        
    st.write("---")
    
    # selezione del modello
    model = st.selectbox(
        "Seleziona il modello:",
        ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        index=1  # predefinito gpt-4o-mini
    )
    
    st.write("---")
    
    # verifica della chiave api
    if not os.getenv("OPENAI_API_KEY"):
        st.error("setta la chiave OPENAI_API_KEY")
        return
    
    if st.button("Generate Quiz"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # creazione event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # elaborazione dei pdf se presenti
            if uploaded_files:
                total_files = len(uploaded_files)
                for file_index, pdf_file in enumerate(uploaded_files):
                    status_text.text(f"elaborazione del pdf {file_index+1} di {total_files}: {pdf_file.name}")
                    progress_bar.progress(file_index / total_files)
                    
                    # salvataggio temporaneo del file caricato
                    temp_path = f"temp_{pdf_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(pdf_file.getbuffer())
                    
                    try:
                        # estrazione del testo dal pdf
                        pdf_text = extract_text_from_pdf(temp_path)
                        if not pdf_text:
                            st.error(f"impossibile estrarre il testo da {pdf_file.name}")
                            continue
                        
                        # salvo testo raw
                        base_filename = pdf_file.name.replace('.pdf', '')
                        raw_text_path = os.path.join(RAW_TEXT_DIR, f"{base_filename}.txt")
                        save_text_to_file(pdf_text, raw_text_path)
                        
                        # elaborazione del testo con gli agenti
                        quiz, base_filename = loop.run_until_complete(
                            create_quiz_from_text(pdf_text, model, pdf_file.name)
                        )
                        
                        if quiz:
                            # salvataggio del quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # visualizzazione del quiz in streamlit
                            st.write(f"### quiz per {base_filename}")
                            for question_index, question in enumerate(quiz.questions, 1):
                                st.write(f"\n**domanda {question_index}:** {question.question_text}")
                                for answer in question.answers:
                                    st.write(f"- ({answer.score} punti) {answer.text}")
                            
                            st.write("---")
                    
                    finally:
                        # pulizia file temporaneo
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            
            # elaborazione degli url se presenti
            if urls_list:
                total_urls = len(urls_list)
                for url_index, url in enumerate(urls_list):
                    status_text.text(f"elaborazione dell'url {url_index+1} di {total_urls}: {url}")
                    progress_bar.progress(url_index / total_urls)
                    
                    try:
                        # estrazione del testo dall'url
                        url_text = extract_text_from_url(url)
                        if not url_text:
                            st.error(f"impossibile estrarre il testo da {url}")
                            continue
                        
                        # estrazione del nome file dall'url
                        base_filename = get_filename_from_url(url)
                        
                        # salvataggio testo raw
                        raw_text_path = os.path.join(RAW_TEXT_DIR, f"{base_filename}.txt")
                        save_text_to_file(url_text, raw_text_path)
                        
                        # elaborazione del testo con gli agenti
                        quiz, base_filename = loop.run_until_complete(
                            create_quiz_from_text(url_text, model, base_filename)
                        )
                        
                        if quiz:
                            # salvataggio del quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # visualizzazione del quiz
                            st.write(f"### quiz per {url}")
                            for question_index, question in enumerate(quiz.questions, 1):
                                st.write(f"\n**domanda {question_index}:** {question.question_text}")
                                for answer in question.answers:
                                    st.write(f"- ({answer.score} punti) {answer.text}")
                            
                            st.write("---")
                    
                    except Exception as e:
                        st.error(f"errore nell'elaborazione dell'url {url}: {str(e)}")
                        logging.error(f"errore nell'elaborazione dell'url {url}: {str(e)}")
                        logging.error(traceback.format_exc())
            
            status_text.text("elaborazione completata!")
            progress_bar.progress(1.0)
            
        except Exception as e:
            st.error(f"si è verificato un errore: {str(e)}")
            logging.error(f"errore nel ciclo principale di elaborazione: {str(e)}")
            logging.error(traceback.format_exc())
        
        finally:
            # chiusura event loop
            loop.close()
        
        st.success("tutti i file sono stati elaborati!")

if __name__ == "__main__":
    main() 