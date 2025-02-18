import os
from crewai.tools import BaseTool
import json
from pydantic import BaseModel, Field
from typing import List

class QuestionOptions(BaseModel):
    A: str = Field(..., description="First option")
    B: str = Field(..., description="Second option")
    C: str = Field(..., description="Third option")
    D: str = Field(..., description="Fourth option")

class Question(BaseModel):
    question: str = Field(..., description="The question text")
    options: QuestionOptions = Field(..., description="The 4 possible answers")
    correct_answer: str = Field(..., description="The correct answer (A, B, C, or D)")

class TopicQuestions(BaseModel):
    topic_file: str = Field(..., description="The filename of the topic (e.g., 'topic_1.txt')")
    questions: List[Question] = Field(..., description="List of questions for this topic")

class TxtToQuestionsTool(BaseTool):
    name: str = "Text to Questions Converter"
    description: str = (
        "A tool for converting text content into multiple-choice questions. "
        "Input must be a JSON string with this exact structure:\n"
        "{\n"
        "  'topic_file': 'topic_1.txt',\n"
        "  'questions': [\n"
        "    {\n"
        "      'question': 'What is X?',\n"
        "      'options': {\n"
        "        'A': 'First option',\n"
        "        'B': 'Second option',\n"
        "        'C': 'Third option',\n"
        "        'D': 'Fourth option'\n"
        "      },\n"
        "      'correct_answer': 'A'\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "IMPORTANT: Use the exact filename format 'topic_X.txt' where X is the topic number."
    )

    def _run(self, topic_file: str = None, questions: List[dict] = None):
        try:
            # input data structure
            input_data = TopicQuestions(
                topic_file=topic_file,
                questions=[Question(**q) for q in questions] if questions else []
            )
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            
            # read the content of the topic file
            input_path = os.path.join(project_root, "output", "divided_topics", input_data.topic_file)
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()

            # create output directory for questions if it doesn't exist
            output_dir = os.path.join(project_root, "output", "questions")
            os.makedirs(output_dir, exist_ok=True)

            # get topic number from filename
            topic_num = input_data.topic_file.split("_")[1].split(".")[0]
            
            # save questions to a json
            output_file = os.path.join(output_dir, f"questions_topic_{topic_num}.json")
            
            # questions data structure
            data = {
                "topic": topic_num,
                "content": content,
                "questions": [q.model_dump() for q in input_data.questions] # creates a json for each question
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return f"Successfully saved questions for topic {topic_num}"

        except Exception as e:
            return f"Error: {str(e)}" 