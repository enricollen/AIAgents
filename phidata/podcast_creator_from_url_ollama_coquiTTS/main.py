import os
from agents.news_scraper import NewsScraper
from agents.news_rewriter import NewsRewriter
from agents.podcast_writer import PodcastWriter
from agents.podcast_audio_generator import PodcastAudioGenerator
from dotenv import load_dotenv

load_dotenv()

NEWS_URL = str(os.getenv('NEWS_URL'))
NUMBER_OF_DIALOGS = int(os.getenv('NUMBER_OF_DIALOGS'))


class PodcastManager:
    def __init__(self):
        self.news_scraper = NewsScraper()
        self.news_rewriter = NewsRewriter()
        self.podcast_dialogues_writer = PodcastWriter()
        self.podcast_audio_generator = PodcastAudioGenerator()

    def run(self, url, host_character, guests, personas, number_of_dialogs):
        print("Scraping news content...")
        raw_news = self.news_scraper.run(url)
        if not raw_news:
            print("Failed to scrape news content. Exiting...")
            return

        print("Rewriting news content...")
        rewritten_news = self.news_rewriter.run(raw_news)
        if not rewritten_news:
            print("Failed to rewrite news content. Exiting...")
            return
        # Save to news.txt
        content_file = "outputs/news.txt"
        print("Saving rewritten news content to file...")
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(str(rewritten_news))
            

        # Restore the news content from file
        """content_file = "outputs/news.txt"
        rewritten_news = ""
        if os.path.exists(content_file):
            print("Loading rewritten news content from file...")
            with open(content_file, 'r', encoding='utf-8') as f:
                rewritten_news = f.read()
        print(str(rewritten_news[:500])+"...\n\n")"""
        

        print("Generating podcast transcript...")
        dialogues = self.podcast_dialogues_writer.run(host_character, rewritten_news, guests, personas, number_of_dialogs)
        if not dialogues:
            print("Failed to generate podcast transcript. Exiting...")
            return
        print("Podcast transcript generated successfully.")
        print(str(dialogues[:500])+"...\n\n")

        print("Generating podcast audio...")
        audio_response = self.podcast_audio_generator.run(str(dialogues))
        if audio_response:
            print(f"Podcast generated successfully.")
        else:
            print("Failed to generate podcast audio.")

if __name__ == "__main__":
    host_character = "Mia"
    guests = ["Nimbus"]
    personas = {
        "Nimbus": "A digital marketer specializing in social media."
    }

    manager = PodcastManager()
    manager.run(NEWS_URL, host_character, guests, personas, NUMBER_OF_DIALOGS)