import os
import streamlit as st
from crewai import Crew, Agent, Task, LLM, Process
from crewai_tools import ScrapeWebsiteTool
from src.podcast_creator_from_url_ollama_coquiTTS.tools.text_to_speech_tool import TextToSpeechTool
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Podcast Creator", layout="centered")
st.title("🎙️ Podcast Creator")

# User inputs: LLM model, News Website URL, and Language selection
llm_model = st.text_input("Enter LLM Model (e.g., ollama/llama3.1:8b):", placeholder="ollama/llama3.1:8b")
website_url = st.text_input("Enter Website URL to scrape content:")

# Language selection
language_options = ["Italian", "English", "Spanish", "French", "German"]
selected_language = st.selectbox("Select Language:", language_options)

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
            goal=f"Extract the main content of the specified website URL: {{website_url}}, ensuring the content is in {selected_language}.",
            backstory=(
                "You're an expert in scraping and extracting meaningful information from web pages. "
                f"You ensure the scraped content is clean, relevant, and easy to process, always ensuring it is in {selected_language}."
            ),
            tools=[website_scraper_tool],
            llm=llm
        )

        reporting_analyst = Agent(
            role="Senior Reporting Analyst",
            goal=f"Create detailed reports based on received content, analyzing data and findings, ensuring all content is in {selected_language}.",
            backstory=(
                "You're a meticulous analyst with a keen eye for detail, especially when it comes to statistics and data. "
                f"You are skilled in transforming complex information into structured reports, always in {selected_language}. "
                "If there is only one major topic, produce a detailed and in-depth report focusing on all relevant aspects. "
                "If there are multiple topics, generate a report that provides key insights and essential highlights for each one in numbered sections."
            ),
            llm=llm
        )

        podcast_writer = Agent(
            role="Podcast Script Writer",
            goal=f"Convert the processed content into a structured podcast conversation in {selected_language}.",
            backstory=(
                f"You're a skilled content creator with experience in writing engaging and natural podcast dialogues in {selected_language}."
            ),
            llm=llm
        )

        audio_generator = Agent(
            role="Audio Producer",
            goal=f"Generate an mp3 audio file from the podcast script in {selected_language}.",
            backstory=(
                "You're an expert in text-to-speech synthesis and audio production. "
                f"You ensure that the podcast narration is of high quality and is produced in {selected_language}."
            ),
            tools=[TextToSpeechTool()],
            output_file="podcasts/podcast.mp3",
            llm=llm
        )

        # Define tasks
        fetch_content_task = Task(
            description=(
                f"Scrape and clean content from the specified website URL: {{website_url}}. "
                f"Extract all relevant details and maintain the context. The language MUST be {selected_language}."
            ),
            expected_output=f"A full report with the main topics, in {selected_language}.",
            agent=website_scraper
        )

        reporting_task = Task(
            description=(
                "Review the scraped content and expand each topic into a full section. "
                "If there is only one major topic, produce a detailed and in-depth report focusing on all relevant aspects. "
                "If there are multiple different topics, generate a report that provides key insights and essential highlights for each one."
            ),
            expected_output=f"A detailed report in {selected_language} with around 6 paragraphs.",
            agent=reporting_analyst
        )

        script_task = Task(
            description=(
                f"Write a podcast script based on the processed content: {{content}}. "
                f"Ensure the script is structured as a natural dialogue and is in {selected_language}. "
                "If there are multiple topics, produce a smaller script for each."
            ),
            expected_output=f"A structured podcast script with a single speaker in {selected_language}.",
            agent=podcast_writer
        )

        audio_task = Task(
            description=(
                f"Generate an mp3 audio file from the podcast script using text-to-speech synthesis. "
                f"Assume only one speaker. Produce an audio file in {selected_language}."
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