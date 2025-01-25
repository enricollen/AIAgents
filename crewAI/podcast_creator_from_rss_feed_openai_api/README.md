# 🎙️ Podcast Creator with OpenAI API Integration

This project demonstrates a **podcast creation pipeline** utilizing:
- **OpenAI API** for processing text and generating podcast scripts.
- **OpenAI TTS** or **ElevenLabs TTS** for high-quality audio generation.

The application automates the workflow of transforming news content **from an RSS feed URL** into a structured podcast with engaging narration. It leverages the modular design of agents and tasks, orchestrated seamlessly by the **CrewAI framework**.

Additionally, this project demonstrates how two distinct crews within CrewAI can interact, making it a versatile example for adapting to other multi-agent use cases.

---

## 🧩 Components and Interactions

### 1. 👥 News Processing Crew
This crew focuses on extracting and analyzing content from the provided RSS feed.

#### **Agents**
- **Senior News Researcher:** 
  - Role: Parse and clean news articles from the RSS feed.
  - Tools: Uses the `NewsParserTool` for efficient RSS feed parsing.
  - Output: Cleaned and relevant news content in Italian.

- **Senior Reporting Analyst:** 
  - Role: Analyze the news content and generate a detailed report.
  - Skills: Expertise in turning complex data into clear, actionable reports.

#### **Tasks**
1. **Fetch News Articles:**
   - Description: Parse and clean up to a specified number of news articles from the RSS feed. Enrich descriptions by extracting relevant details from the associated links.
   - Expected Output: A full report with main topics in Italian.

2. **Content Reporting:**
   - Description: Expand each topic into detailed sections or provide key insights for multiple topics.
   - Expected Output: A detailed report in Italian with approximately six paragraphs.

---

### 2. 👥 Podcast Creation Crew
This crew converts the processed news content into a podcast script and generates the final audio file.

#### **Agents**
- **Podcast Script Writer:** 
  - Role: Convert the processed news into a structured and engaging podcast script.
  - Output: A natural, dialogue-based script in Italian.

- **Audio Producer:** 
  - Role: Generate high-quality MP3 audio from the podcast script using ElevenLabs TTS API.
  - Tools: Uses `TextToSpeechTool` for audio synthesis (using openAI API or Elevenlabs API, it's up to you)
  - Output: An MP3 file of the podcast narration.

#### **Tasks**
1. **Script Writing:**
   - Description: Create a structured podcast script based on the processed news content.
   - Expected Output: A podcast script in Italian with a single speaker.

2. **Audio Generation:**
   - Description: Convert the podcast script into an MP3 audio file.
   - Expected Output: A high-quality MP3 file (`podcasts/podcast_{timestamp}.mp3`).

---

## 🛠️ How It Works

### Step 1: Input RSS Feed URL
The user specifies an RSS feed URL and the number of news articles to fetch.

### Step 2: News Processing Crew
The **News Processing Crew** handles:
1. **Fetching Articles:** Parsing and cleaning news articles from the RSS feed.
2. **Reporting:** Generating a detailed report based on the parsed content.

### Step 3: Podcast Creation Crew
The **Podcast Creation Crew** takes the processed news and performs:
1. **Script Writing:** Crafting a structured podcast script in Italian.
2. **Audio Generation:** Converting the script into an audio file (MP3) using ElevenLabs TTS.

### Step 4: Save Results
- The **parsed news** is saved locally for traceability.
- The **podcast audio** is saved as an MP3 file in the `podcasts` directory.

---

## 📁 Project Structure

```plaintext
.
├── src/
│   ├── podcast_creator_from_rss_feed_openai_api/
│   │   ├── tools/
│   │   │   ├── news_parser_tool.py               # RSS feed parser
│   │   │   └── text_to_speech_tool_elevenlabs.py # ElevenLabs TTS integration
|   |   |   └── text_to_speech_tool.py            # OpenAI TTS integration
│   │   └── main.py                               # Main script
|   |   └── streamlit_app.py                      # Streamlit app
│   └── ...
├── news/
│   ├── news_result.txt                          # Saved news content from the parsing task
├── podcasts/
│   ├── podcast.mp3                              # Generated podcast audio file
├── README.md                                    # Project documentation
```
---
## 🚀 How to Run

1. **Install FFmpeg**:

   - Download FFmpeg from the [official FFmpeg website](https://ffmpeg.org/download.html) or use a package manager suitable for your operating system.
   - Add FFmpeg to your system's PATH:
     - **Windows**: Add the `bin` directory of FFmpeg to your system's environment variables under the `Path`.
     - **Linux/MacOS**: Install FFmpeg using a package manager (e.g., `apt install ffmpeg` on Ubuntu or `brew install ffmpeg` on macOS) and ensure it's accessible in the terminal.
   - Verify installation:
     ```bash
     ffmpeg -version
     ```
     If the command outputs the version details, FFmpeg is correctly installed and configured.

2. Make sure Ollama is running on your system
3. **Clone the repository**:
   ```bash
   git clone https://github.com/enricollen/AIAgents
   cd crewAI/podcast_creator_from_rss_feed_openai_api
   ```
4. **Create and activate a virtual environment to manage dependencies cleanly**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/MacOS
   venv\Scripts\activate      # On Windows
   ```
5. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. Create a .env file in the project root path (see .env_example for reference) and configure environment variables:
   ```plaintext
   OPENAI_API_KEY=YOUR_KEY_HERE
   ELEVENLABS_API_KEY=YOUR_KEY_HERE
   MODEL=gpt-4o-mini
   RSS_FEED_URL=YOUR_RSS_URL_HERE 
   HOW_MANY_NEWS_TO_FETCH=1
   HOW_MANY_PARAGRAPHS_TO_FETCH=13
   ```
7. Run the main.py:
   ```python
   cd src/podcast_creator_from_rss_feed_openai_api
   python main.py
   ```
   or launch the Streamlit app for UI:
   ```python
   cd src/podcast_creator_from_rss_feed_openai_api
   streamlit run streamlit_app.py
   ```

