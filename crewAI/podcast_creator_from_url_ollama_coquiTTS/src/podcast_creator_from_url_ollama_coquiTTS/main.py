import os
from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import ScrapeWebsiteTool
from src.podcast_creator_from_url_ollama_coquiTTS.tools.text_to_speech_tool import TextToSpeechTool
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = str(os.getenv("LLM_MODEL"))
WEBSITE_URL = str(os.getenv("WEBSITE_URL"))

llm = LLM(model=LLM_MODEL, base_url="http://localhost:11434")

website_scraper_tool = ScrapeWebsiteTool(website_url=WEBSITE_URL)

# Agent for website scraping
website_scraper = Agent(
    role="Website Content Scraper",
    goal="Extract the main content of the specified website URL: {website_url}.",
    backstory=(
        "You're an expert in scraping and extracting meaningful information from web pages. "
        "You ensure the scraped content is clean, relevant, and easy to process for further tasks."
    ),
    tools=[website_scraper_tool],
    llm=llm 
)

# Agent for reporting
reporting_analyst = Agent(
    role="Senior Reporting Analyst",
    goal="Create detailed reports based on received content, analyzing data and findings.",
    backstory=(
        "You're a meticulous analyst with a keen eye for detail, especially when it comes to statistics and data. "
        "You're known for your ability to turn complex data into clear and concise reports, making it easy "
        "for others to understand and act on the information you provide. "
        "If there is only one major topic, produce a detailed and in-depth report focusing on all relevant aspects. "
        "If there are multiple topics, generate a report that provides key insights and essential highlights for each one in numbered sections."
    ),
    llm=llm
)

# Task for website content scraping
fetch_content_task = Task(
    description=(
        "Scrape and clean content from the specified website URL: {website_url}. "
        "Extract all relevant details and maintain the context. "
        "The language MUST be Italian."
    ),
    expected_output="A full report with the main topics, in Italian.",
    agent=website_scraper
)

# Task for content reporting
reporting_task = Task(
    description=(
        "Review the scraped content and expand each topic into a full section. "
        "If there is only one major topic, produce a detailed and in-depth report focusing on all relevant aspects. "
        "If there are multiple different topics, generate a report that provides key insights and essential highlights for each one."
    ),
    expected_output="A detailed report in Italian with around 6 paragraphs.",
    agent=reporting_analyst
)

# Agent for podcast script writing
podcast_writer = Agent(
    role="Podcast Script Writer",
    goal="Convert the processed content into a structured podcast conversation.",
    backstory=(
        "You're a skilled content creator with experience in writing engaging and natural podcast dialogues."
    ),
    llm=llm
)

# Agent for audio generation
audio_generator = Agent(
    role="Audio Producer",
    goal="Generate an mp3 audio file from the podcast script.",
    backstory=(
        "You're an expert in text-to-speech synthesis and audio production. "
        "You ensure that the podcast has high-quality narration."
    ),
    tools=[TextToSpeechTool()],
    output_file="podcasts/podcast.mp3",
    llm=llm  
)

# Task for podcast script writing
script_task = Task(
    description=(
        "Write a podcast script based on the processed content: {content}. "
        "Ensure the script is structured as a natural dialogue and is in Italian. "
        "If there are multiple topics, produce a smaller script for each. "
    ),
    expected_output="A structured podcast script with a single speaker in Italian.",
    agent=podcast_writer
)

# Task for audio generation
audio_task = Task(
    description=(
        "Generate an mp3 audio file from the podcast script using text-to-speech synthesis. "
        "Assume only one speaker. Produce an audio file."
    ),
    expected_output="podcasts/podcast.mp3",
    agent=audio_generator
)

# Crew for content processing
content_crew = Crew(
    agents=[website_scraper, reporting_analyst],
    model=llm,  
    tasks=[fetch_content_task, reporting_task],
    cache=True,
    verbose=True,
    process=Process.sequential,
    planning=True,
    planning_llm=llm
)

# Crew for podcast creation
podcast_crew = Crew(
    agents=[podcast_writer, audio_generator],
    model=llm,
    tasks=[script_task, audio_task],
    cache=True,
    verbose=True,
    process=Process.sequential,
    planning=True,
    planning_llm=llm
)

if __name__ == "__main__":
    # First crew for content processing
    content_result = content_crew.kickoff(inputs={"website_url": WEBSITE_URL})

    # dump news scraping result
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file = "output/scraped_news.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(str(content_result))
    
    # restore news scraping result
    """
    output_file = "output/scraped_news.txt"
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            content_result = file.read()
        #print("Restored Content Result from file:", content_result)
    else:
        print(f"Error: File {output_file} does not exist. Ensure content was previously saved.")
        exit(1)
    """
        
    # Second crew for podcast creation
    podcast_result = podcast_crew.kickoff(inputs={"content": content_result})
    print("Podcast Generation Result:", podcast_result)