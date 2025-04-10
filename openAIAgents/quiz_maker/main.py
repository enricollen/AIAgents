import os
import json
import logging
import traceback
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from excel_converter import QuizExcelConverter
from ai_agent import QuizGenerator
from utils import (
    setup_logging, 
    setup_directories, 
    extract_text_from_pdf, 
    save_text_to_file, 
    extract_text_from_url, 
    get_filename_from_url
)

load_dotenv()

nest_asyncio.apply()

# logging
log_filename = setup_logging()

# directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_TEXT_DIR, SUMMARY_TEXT_DIR, JSON_OUTPUT_DIR = setup_directories(BASE_DIR)

def main():
    st.title("Quiz Generator")
    
    st.write("""
    Instructions:
    1. Upload PDF files or enter a list of URLs to generate quizzes from
    2. Files are analyzed and summarized
    3. Quizzes are generated in JSON format and available in Excel format for download
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
    
    # option for combined excel file
    combine_excel = st.checkbox("Create a single Excel file with all quizzes", value=True)
    
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
        
        excel_converter = QuizExcelConverter(BASE_DIR)
        quiz_generator = QuizGenerator(model, SUMMARY_TEXT_DIR)
        
        # store all quizzes for combined export
        all_quizzes = []
        
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
                            quiz_generator.create_quiz_from_text(pdf_text, pdf_file.name, language)
                        )
                        
                        if quiz:
                            # save quiz for combined export
                            all_quizzes.append((quiz, base_filename))
                            
                            # save quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # notify about summary
                            st.info(f"Summary saved in: {os.path.join(SUMMARY_TEXT_DIR, f'{base_filename}_summary.txt')}")
                            
                            if not combine_excel:
                                # convert to excel (individual file)
                                excel_path = excel_converter.json_to_excel(quiz, base_filename)
                                if excel_path:
                                    st.info(f"Excel quiz saved in: {excel_path}")
                                    
                                    # download button
                                    excel_buffer = excel_converter.get_excel_download_buffer(quiz)
                                    st.download_button(
                                        label=f"Download {base_filename} Quiz (Excel)",
                                        data=excel_buffer,
                                        file_name=f"{base_filename}_quiz.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            
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
                            quiz_generator.create_quiz_from_text(url_text, base_filename, language)
                        )
                        
                        if quiz:
                            # save quiz for combined export
                            all_quizzes.append((quiz, base_filename))
                            
                            # save quiz in json
                            output_path = os.path.join(JSON_OUTPUT_DIR, f"{base_filename}_quiz.json")
                            with open(output_path, "w") as f:
                                json.dump(quiz.model_dump(), f, indent=2, ensure_ascii=False)
                            
                            # notify about summary
                            st.info(f"Summary saved in: {os.path.join(SUMMARY_TEXT_DIR, f'{base_filename}_summary.txt')}")
                            
                            if not combine_excel:
                                # convert to excel (individual file)
                                excel_path = excel_converter.json_to_excel(quiz, base_filename)
                                if excel_path:
                                    st.info(f"Excel quiz saved in: {excel_path}")
                                    
                                    # download button
                                    excel_buffer = excel_converter.get_excel_download_buffer(quiz)
                                    st.download_button(
                                        label=f"Download {base_filename} Quiz (Excel)",
                                        data=excel_buffer,
                                        file_name=f"{base_filename}_quiz.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            
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
            
            # create combined excel file if requested and there are quizzes
            if combine_excel and all_quizzes:
                combined_buffer = excel_converter.combine_quizzes_to_excel(all_quizzes)
                
                # download button for combined file
                st.download_button(
                    label="Download Combined Quiz (Excel)",
                    data=combined_buffer,
                    file_name="quiz.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # also save to file system
                combined_path = os.path.join(excel_converter.excel_output_dir, "quiz.xlsx")
                with open(combined_path, "wb") as f:
                    f.write(combined_buffer.getbuffer())
                st.info(f"Sequential numbered quiz saved in: {combined_path}")
            
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