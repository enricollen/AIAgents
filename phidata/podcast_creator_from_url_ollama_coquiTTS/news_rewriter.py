import os
from phi.agent import Agent
from phi.model.ollama import Ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = str(os.getenv('OLLAMA_MODEL'))

class NewsRewriter:
    def __init__(self):
        self.agent = Agent(
            model=Ollama(id=OLLAMA_MODEL),
            instructions=[
                "You are a professional news editor and writer.",
                "Your task is to take raw news content and rewrite it in a clearer, more engaging, and concise format.",
                "The language MUST be Italian."
            ],
            show_tool_calls=True,
        )

    def run(self, raw_news):
        """Processes and rewrites raw news content to improve clarity and engagement."""
        response = self.agent.run(
            f"Take the following raw news content and rewrite it clearly: {raw_news}",
            temperature=0.8,
        )
        print(response.content[:1000] + "...\n\n")
        return response.content if response else None
