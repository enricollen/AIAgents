# USEFUL DOCS LINK FOR CUSTOM TOOLS DEFINITION: https://docs.phidata.com/tools/functions

import os
import subprocess
import time
import torch
from TTS.api import TTS
from phi.agent import Agent
from phi.model.ollama import Ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = str(os.getenv('OLLAMA_MODEL'))

class PodcastAudioGenerator:
    def __init__(self):
        self.agent = Agent(
            model=Ollama(id=OLLAMA_MODEL),
            instructions=[
                "You are an audio podcast creator.",
                "You have a custom tool to generate audio files from the podcast dialogues.",
                "Use the tool 'generate_audio' to generate audio files from the podcast dialogues.",
            ],
            tools=[self.generate_audio],
            show_tool_calls=True,
        )
        
    def run(self, dialogues):
        return self.agent.run(f"Generate a podcast audio file from the following dialogues: {dialogues}") # here is the magic should happen, theoretically the llm should look at the available tools and choose to use them simply from textual prompt
        # If using the run method above doesn't produce the final audio file, uncomment the line below and call the generate_audio method explicitly.
        # Some smaller models like llama3.1:8b may not always understand that the tool is available, so you may need to call the generate_audio method explicitly bypassing the "tools" method.
        #return self.generate_audio(dialogues)
        
    def generate_audio(self, dialogues: str) -> str:
        """Generates audio files from the podcast transcript."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        os.environ["TTS_LICENSE"] = "1"
        tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        dialog_files = []
        os.makedirs("dialogs", exist_ok=True)
        concat_file = open("concat.txt", "w")

        dialogue_lines = dialogues.split("\n")
        for i, dialogue in enumerate(dialogue_lines):
            if not dialogue.strip():
                continue
            try:
                speaker, text = dialogue.split(":", 1)
                speaker = speaker.strip("*").strip()
                text = text.strip()
            except ValueError:
                print(f"Skipping malformed dialogue line: {dialogue}")
                continue

            speaker_wav_path = f"voices/{speaker}.wav"
            if not os.path.exists(speaker_wav_path):
                print(f"Speaker WAV file not found for {speaker}: {speaker_wav_path}")
                continue

            filename = f"dialogs/dialog{i}.wav"
            try:
                tts_model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav_path,
                    language="it",
                    file_path=filename,
                )
                concat_file.write(f"file {filename}\n")
                dialog_files.append(filename)
            except Exception as e:
                print(f"Failed to generate audio for dialogue line {i}: {dialogue}. Error: {e}")

        concat_file.close()

        if not dialog_files:
            print("No dialog files were generated. Exiting audio generation.")
            return None

        podcast_file = f"podcasts/podcast_{time.time()}.wav"
        os.makedirs("podcasts", exist_ok=True)
        try:
            result = subprocess.run(
                f"ffmpeg -f concat -safe 0 -i concat.txt -c copy {podcast_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr.decode()}")
                return None
        except Exception as e:
            print(f"Failed to concatenate audio files. Error: {e}")
            return None

        if not os.path.exists(podcast_file):
            print(f"Failed to generate podcast file: {podcast_file}")
            return None

        os.unlink("concat.txt")
        for file in dialog_files:
            os.unlink(file)

        print(f"Generated podcast file: {podcast_file}")
        return podcast_file