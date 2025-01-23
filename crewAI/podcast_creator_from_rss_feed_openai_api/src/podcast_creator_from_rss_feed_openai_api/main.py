import os
from crewai import Crew, Agent, Task
from dotenv import load_dotenv
from src.podcast_creator_from_rss_feed_openai_api.tools.news_parser_tool import NewsParserTool
from src.podcast_creator_from_rss_feed_openai_api.tools.text_to_speech_tool_elevenlabs import TextToSpeechTool

load_dotenv()

RSS_FEED_URL = str(os.getenv("RSS_FEED_URL"))
HOW_MANY_NEWS_TO_FETCH = int(os.getenv("HOW_MANY_NEWS_TO_FETCH"))

# Agents for news parsing and reporting
news_parser = Agent(
    role="Senior News Researcher",
    goal="Extract latest news articles from the RSS feed {rss_url}.",
    backstory=(
        "You're an expert in parsing and cleaning RSS feed news articles. "
        "Known for your ability to find the most relevant information and present it in a clear and concise manner."
    ),
    tools=[NewsParserTool()]
)

reporting_analyst = Agent(
    role="Senior Reporting Analyst",
    goal="Create detailed reports based on received news, analyzing data and research findings.",
    backstory=(
        "You're a meticulous analyst with a keen eye for detail, especially when it comes to statistics and numbers. "
        "You're known for your ability to turn complex data into clear and concise reports, making "
        "it easy for others to understand and act on the information you provide. "
        "If there is only one news item, produce a detailed and in-depth report focusing on all relevant aspects. "
        "If there are multiple different news, generate a report that provides key insights and essential highlights for each one in numbered sections."
    )
)


# Tasks for news processing
fetch_news_task = Task(
    description=(
        "Fetch and clean up to {how_many_news_to_fetch} news articles from the RSS feed {rss_url}. "
        "Extract all the details from the RSS feed and enrich the description from the associated link. "
        "Maintain all the statistics and numbers and finally produce a cleaner version of the news."
    ),
    expected_output=(
        "A full report with the main topics. The language MUST be Italian."
    ),
    agent=news_parser
)

reporting_task = Task(
    description=(
        "Review the context you got and expand each topic into a full section."
        "If there is only one news item, produce a detailed and in-depth report focusing on all relevant aspects."
        "If there are multiple different news, generate a report that provides key insights and essential highlights for each one."
        #"Make sure the report is detailed and contains any and all relevant information."
    ),
    expected_output=(
        #"A fully-fledged report with the main topics, each with a full section of information. "
        "The language MUST be Italian. The report should be around 6 paragraphs."
    ),
    agent=reporting_analyst
)

# Agents for Podcast creation
podcast_writer = Agent(
    role="Podcast Script Writer",
    goal="Convert the processed news into a structured podcast conversation.",
    backstory=(
        "You're a skilled content creator with experience in writing engaging and natural podcast dialogues."
    )
)

audio_generator = Agent(
    role="Audio Producer",
    goal="Generate an mp3 audio file from the podcast script.",
    backstory=(
        "You're an expert in text-to-speech synthesis and audio production. "
        "You ensure that the podcast has high-quality narration with female voice."
    ),
    tools=[TextToSpeechTool()]
)

# Tasks for Podcast generation
script_task = Task(
    description=(
        "Write a podcast script based on the processed news content: {news_content}. "
        "Ensure the script is structured as a natural dialogue and is in Italian."
        "If there are multiple news articles, produce a smaller script for each."
        "Always start the script saying the name of the podcast: 'SaniTrend di Helaglobe'."
    ),
    expected_output="A structured podcast script with a single speaker in Italian.",
    agent=podcast_writer
)

audio_task = Task(
    description=(
        "Generate an audio file from the podcast script using text-to-speech synthesis and save it in podcasts path. "
        "Assume only one speaker."
        "Produce an audio file."
    ),
    expected_output="podcasts/podcast.mp3",
    agent=audio_generator
)


if __name__ == "__main__":
    # First crew for news gathering
    news_crew = Crew(agents=[news_parser, reporting_analyst], tasks=[fetch_news_task, reporting_task])
    news_result = str(news_crew.kickoff(inputs={"rss_url": RSS_FEED_URL, "how_many_news_to_fetch": HOW_MANY_NEWS_TO_FETCH}))
    print("News Result:", news_result)
    if not os.path.exists("news"): os.makedirs("news")
    output_file = "news/news_result.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(news_result)

    # Restore textual news without calling again the news_crew
    """with open("news/news_result.txt", "r", encoding="utf-8") as file:
        news_result = file.read()"""
    
    # Second crew for Podcast generation
    podcast_crew = Crew(agents=[podcast_writer, audio_generator], tasks=[script_task, audio_task])
    podcast_result = podcast_crew.kickoff(inputs={"news_content": news_result})
    print("Podcast Generation Result:", podcast_result)