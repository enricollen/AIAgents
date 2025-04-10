import logging
import traceback
import os
from typing import Tuple, Optional
from agents import Agent, Runner
from models import Quiz
from utils import save_text_to_file

class QuizGenerator:
    """Class for generating quizzes using AI agents"""
    
    def __init__(self, model: str, summary_dir: str):
        """Initialize the quiz generator
        
        Args:
            model (str): The OpenAI model to use
            summary_dir (str): Directory to save summaries
        """
        self.model = model
        self.summary_dir = summary_dir
        os.makedirs(self.summary_dir, exist_ok=True)
    
    async def create_quiz_from_text(self, text: str, filename: str, language: str) -> Tuple[Optional[Quiz], Optional[str]]:
        """Process a single text document through the agent pipeline
        
        Args:
            text (str): The text to process
            filename (str): The name of the file to process
            language (str): The language to generate the quiz in

        Returns:
            Tuple[Optional[Quiz], Optional[str]]: A tuple containing the quiz and the filename
        """
        try:
            # remove .pdf extension from filename
            base_filename = filename.replace('.pdf', '')
            
            # processing with summarizer agent
            summarizer = Agent(
                name="text summarizer",
                instructions=f"""
                you are an expert at creating detailed summaries of text.
                create a comprehensive summary that capture all important information.
                all summaries must be in {language}.
                maintain the original meaning while making the content more concise.
                """,
                model=self.model
            )
            summary_result = await Runner.run(summarizer, text)
            
            # save summary
            summary_path = os.path.join(self.summary_dir, f"{base_filename}_summary.txt")
            save_text_to_file(summary_result.final_output, summary_path)
            
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
                   - one wrong answer (0 points)
                   - one wrong answer (0 points)
                   - one wrong and potentially harmful answer (-5 points)
                
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
            return None, None 