import os
import re
import time
import subprocess
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from pathlib import Path
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = str(os.getenv("ELEVENLABS_API_KEY"))

class TextToSpeechToolInput(BaseModel):
    """Input schema for TextToSpeechTool."""
    dialogs: list = Field(..., description="List of dialogues for text-to-speech conversion.")

class TextToSpeechTool(BaseTool):
    name: str = "Text-to-Speech Tool"
    description: str = "Generates an audio file from a given list of dialogues using text-to-speech synthesis."
    args_schema: Type[BaseModel] = TextToSpeechToolInput

    def _run(self, dialogs: list):
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        voice_map = {
            "male": "W71zT1VwIFFx3mMGH2uZ",  
            "male2": "uScy1bXtKz8vPzfdFsFw",
            "female": "3DPhHWXDY263XJ1d2EPN"
        }
        
        # Prepare directories
        if not os.path.exists("dialogs"):
            os.makedirs("dialogs")
        dialog_files = []
        concat_file = open("concat.txt", "w")

        cleaned_dialogs = []
        for i, dialog in enumerate(dialogs):
            if isinstance(dialog, str):
                cleaned_dialogs.append({"speaker": "male2", "content": dialog})
            elif isinstance(dialog, dict) and "speaker" in dialog and "content" in dialog:
                cleaned_dialogs.append(dialog)
            else:
                print(f"❌ Skipping invalid dialog entry at index {i}: {dialog}")

        try:
            for i, dialog in enumerate(cleaned_dialogs):
                filename = f"dialogs/dialog{i}.mp3"
                file_path = Path(filename)
                text = dialog["content"]
                cleaned_speaker = re.sub(r"[^a-zA-Z0-9]", "", dialog["speaker"]).strip().lower()
                voice_id = voice_map.get(cleaned_speaker, "uScy1bXtKz8vPzfdFsFw")  # Default voice

                # ElevenLabs TTS
                response = client.text_to_speech.convert(
                    voice_id=voice_id,
                    output_format="mp3_22050_32",
                    text=text,
                    model_id="eleven_multilingual_v2",
                )

                # Save the streaming response to a file
                with open(file_path, "wb") as audio_file:
                    for chunk in response:  # Streamed audio chunks
                        audio_file.write(chunk)

                concat_file.write(f"file '{filename}'\n")
                dialog_files.append(filename)

        except Exception as e:
            print(f"Error during TTS generation: {e}")

        concat_file.close()

        # Concatenate all generated audio files into a single podcast file
        podcast_dir = 'podcasts'
        if not os.path.exists(podcast_dir):
            os.makedirs(podcast_dir)
        podcast_file = f"{podcast_dir}/podcast_elevenlabs{time.time()}.mp3"
        subprocess.run(
            f"ffmpeg -f concat -safe 0 -i concat.txt -c copy {podcast_file}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Cleanup intermediate files
        os.unlink("concat.txt")
        for file in dialog_files:
            os.unlink(file)

        return podcast_file