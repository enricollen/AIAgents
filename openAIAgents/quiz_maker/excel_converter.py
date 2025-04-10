import os
import logging
import traceback
import io
import pandas as pd
from typing import List, Tuple
from models import Quiz

class QuizExcelConverter:
    """Class for converting quiz JSON files to Excel format"""
    
    def __init__(self, base_dir):
        """Initialize the converter
        
        Args:
            base_dir (str): The base directory for the application
        """
        self.excel_output_dir = os.path.join(base_dir, "excel_question_answers")
        os.makedirs(self.excel_output_dir, exist_ok=True)
    
    def json_to_excel(self, quiz: Quiz, filename: str) -> str:
        """Convert a quiz object to Excel format
        
        Args:
            quiz (Quiz): the quiz object to convert
            filename (str): the base filename to use for the Excel file
            
        Returns:
            str: the path to the created Excel file
        """
        try:
            excel_path = os.path.join(self.excel_output_dir, f"{filename}_quiz.xlsx")
            
            # DataFrame to store the quiz
            data = []
            
            # add each question and its answers to the DataFrame
            for i, question in enumerate(quiz.questions, 1):
                # question
                data.append({
                    'Question Number': i,
                    'Theme': question.theme,
                    'Question': question.question_text,
                    'Answer Option': '',
                    'Answer Text': '',
                    'Score': '',
                    'Source': filename
                })
                
                # answers
                for j, answer in enumerate(question.answers, 1):
                    data.append({
                        'Question Number': '',
                        'Theme': '',
                        'Question': '',
                        'Answer Option': f"Option {j}",
                        'Answer Text': answer.text,
                        'Score': answer.score,
                        'Source': ''
                    })
            
            df = pd.DataFrame(data)
            
            # write to Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Quiz')
                
                # column widths
                workbook = writer.book
                worksheet = workbook.active
                for i, col in enumerate(df.columns):
                    column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = min(column_width, 50)  # Limit width to 50
            
            return excel_path
            
        except Exception as e:
            logging.error(f"Error converting quiz to Excel: {str(e)}")
            logging.error(traceback.format_exc())
            return ""
    
    def get_excel_download_buffer(self, quiz: Quiz) -> io.BytesIO:
        """Get a BytesIO buffer containing the Excel file for download
        
        Args:
            quiz (Quiz): the quiz object to convert
            
        Returns:
            io.BytesIO: a buffer containing the Excel file
        """
        try:
            buffer = io.BytesIO()
            
            # DataFrame to store the quiz
            data = []
            
            # add each question and its answers to the DataFrame
            for i, question in enumerate(quiz.questions, 1):
                # question
                data.append({
                    'Question Number': i,
                    'Theme': question.theme,
                    'Question': question.question_text,
                    'Answer Option': '',
                    'Answer Text': '',
                    'Score': ''
                })
                
                # answers
                for j, answer in enumerate(question.answers, 1):
                    data.append({
                        'Question Number': '',
                        'Theme': '',
                        'Question': '',
                        'Answer Option': f"Option {j}",
                        'Answer Text': answer.text,
                        'Score': answer.score
                    })
            
            # DataFrame
            df = pd.DataFrame(data)
            
            # write to Excel buffer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Quiz')
                
                # column widths
                workbook = writer.book
                worksheet = workbook.active
                for i, col in enumerate(df.columns):
                    column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = min(column_width, 50)  # Limit width to 50
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logging.error(f"Error creating Excel download buffer: {str(e)}")
            logging.error(traceback.format_exc())
            return io.BytesIO()
    
    def combine_quizzes_to_excel(self, quizzes: List[Tuple[Quiz, str]]) -> io.BytesIO:
        """Combine multiple quizzes into a single Excel file
        
        Args:
            quizzes (List[Tuple[Quiz, str]]): list of (Quiz, filename) tuples
            
        Returns:
            io.BytesIO: a buffer containing the combined Excel file
        """
        try:
            buffer = io.BytesIO()
            
            # DataFrame to store all quizzes
            all_data = []
            
            # process each quiz
            question_counter = 1  # global counter for question numbers
            
            for quiz, _ in quizzes: 
                # add each question and its answers to the df
                for question in quiz.questions:
                    # question
                    all_data.append({
                        'Question Number': question_counter,
                        'Theme': question.theme,
                        'Question': question.question_text,
                        'Answer Option': '',
                        'Answer Text': '',
                        'Score': ''
                    })
                    
                    # answers
                    for j, answer in enumerate(question.answers, 1):
                        all_data.append({
                            'Question Number': '',
                            'Theme': '',
                            'Question': '',
                            'Answer Option': f"Option {j}",
                            'Answer Text': answer.text,
                            'Score': answer.score
                        })
                    
                    # question counter after adding all answers
                    question_counter += 1
            
            df = pd.DataFrame(all_data)
            
            # Write to Excel buffer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Combined Quiz')
                
                # column widths
                workbook = writer.book
                worksheet = workbook.active
                for i, col in enumerate(df.columns):
                    column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = min(column_width, 50)  # Limit width to 50
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logging.error(f"Error creating combined Excel file: {str(e)}")
            logging.error(traceback.format_exc())
            return io.BytesIO() 