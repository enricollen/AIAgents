from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import List

class Dialogue(BaseModel):
    """
    Represents a dialogue in the podcast transcript.
    It helps with validation and formatting and ensures the speaker name and dialogue text are not empty.
    """
    speaker: str = Field(..., description="The name of the speaker.")
    text: str = Field(..., description="The dialogue text.")

    @field_validator("speaker")
    def speaker_must_be_valid(cls, v: str, info: ValidationInfo) -> str:
        if not v.strip():
            raise ValueError('Speaker name cannot be empty.')
        return v.strip()

    @field_validator("text")
    def text_must_be_valid(cls, v: str, info: ValidationInfo) -> str:
        if not v.strip():
            raise ValueError('Dialogue text cannot be empty.')
        return v.strip()

class PodcastTranscript(BaseModel):
    dialogues: List[Dialogue]

    def to_string(self) -> str:
        return "\n".join(f"**{dialogue.speaker}:** {dialogue.text}" for dialogue in self.dialogues)