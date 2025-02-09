import os
from phi.agent import Agent
from phi.model.ollama import Ollama
from models import PodcastTranscript
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = str(os.getenv('OLLAMA_MODEL'))

class PodcastWriter:
    def __init__(self):
        self.agent = Agent(
            model=Ollama(id=OLLAMA_MODEL),
            instructions=[
                "You are a podcast transcript writer.",
                "Always include detailed dialogues.",
                "Generate the transcript in the following format: **Speaker:** Dialogue text.",
                "Do not include any other text or formatting outside of the dialogues.",
                "Avoid using titles or headings, just the actual speakers and dialogues."
            ],
            show_tool_calls=True,
        )

    def run(self, host_character, news_content, guests, personas, number_of_dialogs):
        character_personas = "\n".join(f"- {guest}: {persona}" for guest, persona in personas.items())
        guest_introductions = ", ".join(guests)

        podcast_template = f"""
        ## Podcast Outline
        This is a podcast between {host_character} and {guest_introductions}.
        **{host_character}** is the interviewer of the show.
        {guest_introductions} are the guests.
        ### Topic of the Podcast:
        {news_content}
        ### Character Personas:
        {character_personas}
        """

        instructions = f"""
        Instructions:
        - The podcast should have around {number_of_dialogs} dialogs. Always include a closure dialog.
        - The entire podcast content MUST be in Italian.
        """

        raw_dialogues_response = self.agent.run(
            f"Generate a podcast transcript for this Podcast Outline: {podcast_template} {instructions}",
            temperature=1,
        )

        # get the content from the RunResponse object
        raw_dialogues = getattr(raw_dialogues_response, 'content', None)
        if not raw_dialogues:
            print("Failed to extract dialogues from the response. Exiting...")
            return None

        # get the raw dialogues into a list of Dialogue objects for Pydantic
        dialogues = self.parse_dialogues(raw_dialogues)

        # Validate and convert to PodcastTranscript
        try:
            podcast_transcript = PodcastTranscript(dialogues=dialogues)
            return podcast_transcript.to_string()
        except Exception as e:
            print(f"Failed to validate podcast transcript: {e}")
            return None

    def parse_dialogues(self, raw_dialogues: str) -> list:
        dialogues = []
        lines = raw_dialogues.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                speaker, text = line.split(":", 1)
                speaker = speaker.strip("*")
                text = text.strip()
                if speaker and text:
                    dialogues.append({"speaker": speaker, "text": text})
            except ValueError:
                print(f"Skipping malformed dialogue line: {line}")
        return dialogues