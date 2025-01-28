import os
import streamlit as st
from crewai import Crew, Agent, Task, LLM, Process
from crewai_tools import ScrapeWebsiteTool
from src.podcast_creator_from_url_ollama_coquiTTS.tools.text_to_speech_tool import TextToSpeechTool
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Podcast Creator", layout="centered")
st.title("🎙️ Podcast Creator")

# user inputs: LLM model and News Website URL
llm_model = st.text_input("Enter LLM Model (e.g., ollama/llama3.1:8b):", placeholder="ollama/llama3.1:8b")
website_url = st.text_input("Enter Website URL to scrape content:")
website_url = str(website_url)

# button to start the process
if st.button("Generate Podcast"):
    if not llm_model or not website_url:
        st.error("Please provide both the LLM model and the website URL.")
    else:
        st.info("📄 Starting the podcast creation process. Please wait...")

        llm = LLM(model=llm_model, base_url="http://localhost:11434")
        website_scraper_tool = ScrapeWebsiteTool(website_url=website_url)

        # Define agents
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

        podcast_writer = Agent(
            role="Podcast Script Writer",
            goal="Convert the processed content into a structured podcast conversation.",
            backstory=(
                "You're a skilled content creator with experience in writing engaging and natural podcast dialogues."
            ),
            llm=llm
        )

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

        # Define tasks
        fetch_content_task = Task(
            description=(
                "Scrape and clean content from the specified website URL: {website_url}. "
                "Extract all relevant details and maintain the context. "
                "The language MUST be Italian."
            ),
            expected_output="A full report with the main topics, in Italian.",
            agent=website_scraper
        )

        reporting_task = Task(
            description=(
                "Review the scraped content and expand each topic into a full section. "
                "If there is only one major topic, produce a detailed and in-depth report focusing on all relevant aspects. "
                "If there are multiple different topics, generate a report that provides key insights and essential highlights for each one."
            ),
            expected_output="A detailed report in Italian with around 6 paragraphs.",
            agent=reporting_analyst
        )

        script_task = Task(
            description=(
                "Write a podcast script based on the processed content: {content}. "
                "Ensure the script is structured as a natural dialogue and is in Italian. "
                "If there are multiple topics, produce a smaller script for each. "
                "Always start the script saying the name of the podcast: 'SaniTrend di Helaglobe'."
            ),
            expected_output="A structured podcast script with a single speaker in Italian.",
            agent=podcast_writer
        )

        audio_task = Task(
            description=(
                "Generate an mp3 audio file from the podcast script using text-to-speech synthesis. "
                "Assume only one speaker. Produce an audio file."
            ),
            expected_output="podcasts/podcast.mp3",
            agent=audio_generator
        )

        # content crew
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

        # podcast crew
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

        # Run crews
        try:
            content_result = content_crew.kickoff(inputs={"website_url": website_url})

            # dump textual scraped news
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "scraped_news.txt")
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(str(content_result))

            st.success("News content successfully scraped and processed.")

            # Podcast generation
            st.info("🎙️ Starting the podcast generation process. Please wait...")
            podcast_result = podcast_crew.kickoff(inputs={"content": str(content_result)})
            st.success("Podcast generated successfully.")

            # audio download link in the UI
            podcast_dir = "podcasts"
            # find the latest .wav created in podcast directory
            latest_podcast_file = max(
                (os.path.join(podcast_dir, f) for f in os.listdir(podcast_dir) if f.endswith(".wav")),
                key=os.path.getmtime,
                default=None 
            )
            if latest_podcast_file and os.path.exists(latest_podcast_file):
                st.audio(latest_podcast_file, format="audio/wav")
                st.download_button(
                    label="Download Podcast",
                    data=open(latest_podcast_file, "rb").read(),
                    file_name=os.path.basename(latest_podcast_file),
                    mime="audio/wav"
                )
            else:
                st.error("No podcast file found. Please ensure the podcast generation was successful.")


        except Exception as e:
            st.error(f"An error occurred: {e}")