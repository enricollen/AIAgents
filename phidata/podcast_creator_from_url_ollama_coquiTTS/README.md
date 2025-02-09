# 🎙️ Podcast Creator with Phidata Agent Framework

This project demonstrates a fully local **podcast creation pipeline** built using the **Phidata Agent Library** and:
- **Ollama** to run local LLMs.
- **Coqui TTS** for audio generation.

The pipeline automates the entire workflow of converting news content from a URL into a podcast with narration. The project showcases modular, reusable components that work seamlessly to produce high-quality podcast outputs.

---

## 🧩 Components and Interactions

The project comprises individual **agents**, each responsible for a specific task in the podcast creation pipeline. Below is the breakdown:

### **1. News Scraper** 🕵️‍♂️
- **Agent Role:** Extract news content from the given URL.
- **Details:**
  - Powered by **Phidata Agent Framework** and uses tools for efficient web scraping.
  - Ensures the scraped content is clean and relevant, with a focus on Italian language content.
- **Key Output:** Raw news content.

### **2. News Rewriter** ✍️
- **Agent Role:** Rewrite and enhance the scraped content for clarity and engagement.
- **Details:**
  - Leverages the power of language models to process raw content into readable, well-structured text.
- **Key Output:** Rewritten news content.

### **3. Podcast Writer** 🗣️
- **Agent Role:** Generate podcast dialogue scripts from rewritten content.
- **Details:**
  - Constructs structured dialogues based on the provided host, guest personas, and rewritten content.
  - Allows customization by specifying the number of dialogues.
- **Key Output:** A podcast transcript in natural dialogue format.

### **4. Podcast Audio Generator** 🎵
- **Agent Role:** Convert the podcast script into an MP3 audio file.
- **Details:**
  - Uses **text-to-speech synthesis** to generate high-quality audio.
- **Key Output:** A podcast MP3 file.

---

## 🛠️ How It Works

### Step 1: Provide a News URL
- The user inputs a URL pointing to a news article. This URL becomes the source for content scraping.

### Step 2: Modular Agent Execution
1. **Scraping:** The **News Scraper** extracts raw content from the URL.
2. **Rewriting:** The **News Rewriter** processes and enhances the scraped content for readability.
3. **Script Writing:** The **Podcast Writer** agent generates a structured dialogue script using the rewritten news.
4. **Audio Generation:** The **Podcast Audio Generator** converts the dialogue script into a podcast MP3 file.

### Step 3: Save Results
- The rewritten content is saved in the `outputs/` directory for traceability.
- The generated podcast MP3 file is saved in the `podcasts/` directory.

---

## 📁 Project Structure

```plaintext
.
├── agents/                      # Folder containing agent scripts
│   ├── news_scraper.py          # Agent for scraping news
│   ├── news_rewriter.py         # Agent for rewriting news
│   ├── podcast_writer.py        # Agent for generating podcast dialogue scripts
│   ├── podcast_audio_generator.py # Agent for generating podcast audio
├── outputs/                     # Directory for storing intermediate results
│   ├── news.txt                 # Rewritten news content
├── podcasts/                    # Directory for storing generated podcasts
│   └── podcast.mp3              # Final podcast MP3 file
├── voices/                      # Contains reference wav files for TTS
├── main.py                      # Main script to execute the pipeline
├── .env_example                 # Example environment configuration file
├── requirements.txt             # Python dependencies
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
   cd phidata/podcast_creator_from_url_ollama_coquiTTS
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
   LLM_MODEL=llama3.1:8b
   WEBSITE_URL=https://example.com/news-article
   ```
7. Run the main.py:
   ```python
   cd src/podcast_creator_from_url_ollama_coquiTTS
   python main.py
   ```

