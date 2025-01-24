import os
from phi.agent import Agent
from phi.model.ollama import Ollama
from phi.tools.crawl4ai_tools import Crawl4aiTools
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = str(os.getenv('OLLAMA_MODEL'))

class NewsScraper:
    def __init__(self):
        self.agent = Agent(
            model=Ollama(id=OLLAMA_MODEL),
            tools=[Crawl4aiTools(max_length=10000)],
            instructions=[
                "You are a professional web scraper.",
                "Your task is to scrape content from the provided URL and return clean, relevant information.",
                "The language MUST be Italian."
            ],
            show_tool_calls=True
        )

    def run(self, url):
        """Scrapes news content from the provided URL."""
        response = self.agent.run(f"Scrape and extract relevant content from this URL: {url}")
        print(response.content[:1000] + "...\n\n")
        return response.content if response else None
