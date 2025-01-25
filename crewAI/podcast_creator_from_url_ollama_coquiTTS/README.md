# 🎙️ Podcast Creator with Fully Local Setup

This project demonstrates a **podcast creation pipeline** using a fully local setup with **Ollama** as the LLM (Large Language Model) and **Coqui TTS** for audio generation. The application automates the process of converting news content from a website into a structured podcast with engaging narration, leveraging the power of modular agents and tasks managed by the **CrewAI framework**. 

---

## 🌟 Key Features
- **Local LLM (Ollama):** For natural language processing tasks such as content extraction, reporting, and podcast script creation.
- **Coqui TTS:** For high-quality text-to-speech audio generation.
- **Modular Task Design:** Agents and tasks are grouped into two distinct crews for content processing and podcast creation.
- **End-to-End Automation:** Users provide a news URL, and the system handles the rest — from web scraping to audio production.
- **Flexible and Scalable:** Easily extendable for more agents, tools, or additional features.

---

## 🛠️ How It Works

### Step 1: Provide a News URL
The user inputs a news URL. This URL becomes the starting point for scraping and processing content.

### Step 2: Content Processing Crew
The **Content Processing Crew** handles:
1. **Scraping:** Extracting and cleaning the main content from the website.
2. **Reporting:** Generating a detailed report based on the scraped content.

### Step 3: Podcast Creation Crew
The **Podcast Creation Crew** takes the processed content and performs:
1. **Script Writing:** Crafting a structured podcast script in Italian.
2. **Audio Generation:** Converting the script into an audio file (MP3) using Coqui TTS.

### Step 4: Save Results
- The **scraped content** is saved locally for traceability.
- The **podcast audio** is saved as an MP3 file in the `podcasts` directory.

---

## 📁 Project Structure

```plaintext
.
├── src/
│   ├── podcast_creator_from_url_ollama_coquiTTS/
│   │   ├── tools/
│   │   │   └── text_to_speech_tool.py  # Coqui TTS integration for audio generation
│   │   └── agents/                     # Custom agents for specific tasks
│   └── ...
├── output/
│   ├── scraped_news.txt                # Saved content from the news scraping task
├── podcasts/
│   ├── podcast.mp3                     # Generated podcast audio file
└── README.md                           # Project documentation
```

---

## 🧩 Components and Interactions

### Content Processing Crew
This crew focuses on extracting and analyzing content from the provided URL.

#### **Agents**
- **Website Content Scraper:** 
  - Role: Extract the main content of the specified website URL.
  - Tools: Uses the `ScrapeWebsiteTool` for efficient web scraping.
  - Output: Cleaned and relevant content in Italian.

- **Senior Reporting Analyst:** 
  - Role: Analyze the scraped content and generate a detailed report.
  - Skills: Expertise in turning complex data into clear, actionable reports.

#### **Tasks**
1. **Scrape Website Content:**
   - Description: Extract and clean the main content from the specified website.
   - Expected Output: A full report with the main topics in Italian.

2. **Content Reporting:**
   - Description: Analyze the scraped content and expand each topic into a detailed section or provide key insights for multiple topics.
   - Expected Output: A detailed report in Italian with approximately six paragraphs.

---

### Podcast Creation Crew
This crew converts processed content into a podcast script and generates the final audio file.

#### **Agents**
- **Podcast Script Writer:** 
  - Role: Convert the processed content into a structured and engaging podcast script.
  - Output: A natural, dialogue-based script in Italian.

- **Audio Producer:** 
  - Role: Generate high-quality MP3 audio from the podcast script.
  - Tools: Uses Coqui TTS for text-to-speech synthesis.
  - Output: An MP3 file of the podcast narration.

#### **Tasks**
1. **Script Writing:**
   - Description: Create a structured podcast script based on the processed content.
   - Expected Output: A podcast script in Italian with a single speaker.

2. **Audio Generation:**
   - Description: Convert the podcast script into an MP3 audio file.
   - Expected Output: A high-quality MP3 file (`podcasts/podcast.mp3`).

---
## 🚀 How to Run

1. Make sure Ollama is running on your system
2. FFmpeg: Install and ensure FFmpeg is added to your system's PATH.
3. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/podcast-creator
   cd podcast-creator
   ```
4. **Python Environment:** Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a .env file and configure environment variables:
   ```plaintext
   LLM_MODEL=llama3.1:8b
    WEBSITE_URL=https://example.com/news-article
    ```
6. Run the main.py:
   ```python
   python main.py
   ```

