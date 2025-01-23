import os
import time
import subprocess
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
from TTS.api import TTS
import torch

class TextToSpeechToolInput(BaseModel):
    """Input schema for TextToSpeechTool."""
    dialogs: List[str] = Field(
        ...,
        description="List of dialogues (strings) for text-to-speech conversion."
    )

class TextToSpeechTool(BaseTool):
    name: str = "Text-to-Speech Tool to generate audio from text"
    description: str = "Generates a mono-speaker podcast audio file from a list of dialogues."
    args_schema: Type[BaseModel] = TextToSpeechToolInput

    def _run(self, dialogs: List[str]):
        # Setup CoquiTTS
        print("Starting TTS...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts_model_path = "tts_models/multilingual/multi-dataset/xtts_v2" 
        tts = TTS(tts_model_path).to(device)

        # Ensure directories exist
        if not os.path.exists("dialogs"):
            os.makedirs("dialogs")

        dialog_files = []
        concat_file = open("concat.txt", "w")

        for i, dialog in enumerate(dialogs):
            if not isinstance(dialog, str) or not dialog.strip():
                print(f"❌ Invalid dialog entry at index {i}: {dialog}")
                continue

            output_file = f"dialogs/dialog{i}.wav"
            try:
                # Generate audio
                tts.tts_to_file(
                    text=dialog,
                    language="it",
                    speaker_wav="voices/Nimbus.wav",
                    file_path=output_file
                )
                concat_file.write(f"file '{output_file}'\n")
                dialog_files.append(output_file)
                print(f"Generated audio for dialog {i}")
            except Exception as e:
                print(f"Error generating audio for dialog {i}: {e}")

        concat_file.close()

        # Combine audio files into a single podcast file
        podcast_dir = 'podcasts'
        if not os.path.exists(podcast_dir):
            os.makedirs(podcast_dir)
        podcast_file = f"{podcast_dir}/podcast{time.time()}.wav"

        try:
            subprocess.run(
                f"ffmpeg -f concat -safe 0 -i concat.txt -c copy {podcast_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"Error combining audio files: {e}")

        # Cleanup
        os.unlink("concat.txt")
        for file in dialog_files:
            os.unlink(file)

        return podcast_file