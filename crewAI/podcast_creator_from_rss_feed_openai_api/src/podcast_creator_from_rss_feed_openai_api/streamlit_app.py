import streamlit as st
import os
from crewai import Crew, Agent, Task
from dotenv import load_dotenv
from src.podcast_creator_from_rss_feed_openai_api.tools.news_parser_tool import NewsParserTool
from src.podcast_creator_from_rss_feed_openai_api.tools.text_to_speech_tool import TextToSpeechTool

load_dotenv()

RSS_FEED_URL = str(os.getenv("RSS_FEED_URL"))
HOW_MANY_NEWS_TO_FETCH = int(os.getenv("HOW_MANY_NEWS_TO_FETCH", 5))

# Define agents
news_parser = Agent(
    role="Senior News Researcher",
    goal="Extract latest news articles from the RSS feed {rss_url}.",
    backstory="You're an expert in parsing and cleaning RSS feed news articles.",
    tools=[NewsParserTool()]
)

reporting_analyst = Agent(
    role="Senior Reporting Analyst",
    goal="Create detailed reports based on received news, analyzing data and research findings.",
    backstory="You're a meticulous analyst with a keen eye for detail, especially with statistics and numbers."
)

podcast_writer = Agent(
    role="Podcast Script Writer",
    goal="Convert the following news into a structured podcast conversation: {news_content}.",
    backstory="You're skilled in writing engaging and natural podcast dialogues."
)

audio_generator = Agent(
    role="Audio Producer",
    goal="Generate an mp3 audio file from the podcast script.",
    backstory="You're an expert in text-to-speech synthesis and audio production.",
    tools=[TextToSpeechTool()]
)

# Define tasks
fetch_news_task = Task(
    description="Fetch and clean up to {how_many_news_to_fetch} news articles from the RSS feed {rss_url}.",
    expected_output="A report with the main topics. The language MUST be Italian.",
    agent=news_parser
)

reporting_task = Task(
    description=(
        "Review the fetched news and expand each topic into a full section. "
        "Generate a detailed report or provide key highlights if there are multiple news items."
    ),
    expected_output="The report should be detailed and in Italian.",
    agent=reporting_analyst
)

script_task = Task(
    description=("Write a podcast script based on this news content: {news_content}."
                "Ensure the script is structured as a dialogue in Italian."
                "If there are multiple news articles, produce a smaller script for each."
                "Always start the script saying the name of the podcast: 'SaniTrend di Helaglobe'."),
    expected_output="A structured podcast script in Italian.",
    agent=podcast_writer
)

audio_task = Task(
    description="Generate an audio file from the podcast script using text-to-speech synthesis.",
    expected_output="podcasts/podcast.mp3",
    agent=audio_generator
)

st.title("Podcast Generator 🌎🎙️")
rss_url = st.text_input("Enter RSS Feed URL:", value=RSS_FEED_URL)

if "news_result" not in st.session_state:
    st.session_state["news_result"] = None
if "podcast_file" not in st.session_state:
    st.session_state["podcast_file"] = None

# Generate News Button
if st.button("Generate News"):
    if rss_url:
        st.write("🔍 Processing news...")
        news_crew = Crew(agents=[news_parser, reporting_analyst], tasks=[fetch_news_task, reporting_task])
        news_result = news_crew.kickoff(inputs={"rss_url": rss_url, "how_many_news_to_fetch": HOW_MANY_NEWS_TO_FETCH})

        # Extract the raw result or handle missing data
        report = None
        try:
            # Look for a "raw" key or use tasks_output
            report = getattr(news_result, "raw", None)
            if not report:
                # Search through task outputs for a valid result
                for task_output in news_result.tasks_output:
                    if task_output.description.startswith("Review the fetched news"):
                        report = task_output.raw
                        break
        except AttributeError:
            st.error("Unexpected structure in news result.")

        if report:
            st.session_state["news_result"] = report
            st.success("News generation completed!")
            st.text_area("Generated News:", report, height=500)
        else:
            st.error("Failed to generate news. Please check the task configuration.")
    else:
        st.error("Please provide a valid RSS Feed URL.")


# Podcast Button
if st.button("Generate Podcast"):
    st.write("🎙 Generating podcast...")

    # check news has been created before proceeding with podcast generation
    if not st.session_state["news_result"]:
        st.error("Please generate the news first.")
    else:
        # trigger the podcast crew
        podcast_crew = Crew(agents=[podcast_writer, audio_generator], tasks=[script_task, audio_task])
        podcast_result = podcast_crew.kickoff(inputs={"news_content": st.session_state["news_result"]})

        podcast_dir = "podcasts"
        if os.path.exists(podcast_dir):
            # get the most recently created MP3 file for playback it in streamlit
            podcast_files = [os.path.join(podcast_dir, f) for f in os.listdir(podcast_dir) if f.endswith(".mp3")]
            if podcast_files:
                podcast_files.sort(key=os.path.getmtime, reverse=True)
                podcast_file = podcast_files[0]
                st.session_state["podcast_file"] = podcast_file
                st.success("Podcast generation completed!")
                st.audio(podcast_file, format="audio/mp3")
            else:
                st.error("No podcast files found in the podcasts directory.")
        else:
            st.error("Podcasts directory does not exist. Please check the generation process.")