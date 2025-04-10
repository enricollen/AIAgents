from typing import List
from pydantic import BaseModel, Field

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
                            {"text": "wrong answer", "score": 0},
                            {"text": "wrong answer", "score": 0},
                            {"text": "very wrong answer", "score": -5}
                        ]
                    }
                ]
            }
        } 