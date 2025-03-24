# 🤖 AI Agents Repository

This repository is a collection of agent-based projects designed to test and showcase the use of agents and workflows across various use cases. Each project explores a unique application of agents to automate processes, leveraging frameworks like **CrewAI**, **Phidata**, and other to come...

---

## 🏗️ Projects Overview

| Project Name                                  | Framework  | Description                                                                                                                                  | Local Setup | API-Based | Outputs                                                                                                                                          |
|----------------------------------------------|------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **[news_reporting](https://github.com/enricollen/AIAgents/tree/main/crewAI/news_reporting)**      | CrewAI     | Designed for generating markdown reports (detailed summaries and bullet points) from RSS feed URL. It can be useful for starting out and to see how to use Custom Tools with CrewAI.              | ❌           | ✅         | Markdown report (`.md`)                                                                                                       |
| **[podcast_creator_from_url_ollama_coquiTTS](https://github.com/enricollen/AIAgents/tree/main/crewAI/podcast_creator_from_url_ollama_coquiTTS)** | CrewAI    | Automates the creation of podcasts from news content scraped from a given URL. Uses **Ollama** for LLM handling and **Coqui TTS** for local audio generation. | ✅           | ❌         | Summarized news content (`.txt`), Podcast audio (`.mp3`)                                                                                         |
| **[podcast_creator_from_rss_feed_openai_api](https://github.com/enricollen/AIAgents/tree/main/crewAI/podcast_creator_from_rss_feed_openai_api)** | CrewAI     | Automates the creation of podcasts from news content scraped from an RSS feed. Uses **OpenAI API** for both textual and audio parts.                              | ❌           | ✅         | Summarized news content (`.txt`), Podcast audio (`.mp3`)   |
| **[quiz_maker](https://github.com/enricollen/AIAgents/tree/main/crewAI/quiz_maker)** | CrewAI     | Automates the creation of quizzes starting from a web page URL. Uses **OpenAI API** for topic extraction and questions/answers generation.                              | ❌           | ✅         | Generate as many quizzes (`.json`) (each containing a question and possible answers) as there are distinct topics found within the URL page.    |
| **[podcast_creator_from_url_ollama_coquiTTS](https://github.com/enricollen/AIAgents/tree/main/phidata/podcast_creator_from_url_ollama_coquiTTS)**| Phidata    | Phidata version of the podcast creator. Uses **Ollama** for LLM handling and **Coqui TTS** for local audio generation.                                       | ✅           | ❌         | Summarized news content (`.txt`), Podcast audio (`.mp3`)                                                                                           |                                                                     |

---
## 📁 Directory Structure

```plaintext
.
├── AIAgents/                                           # Root repository
│   ├── CrewAI/                                         # Projects built using CrewAI framework
│   │   ├── news_reporting/                             # News reporting and summarization
│   │   ├── podcast_creator_from_url_ollama_coquiTTS/   # Local podcast creation using CrewAI
|   |   ├── podcast_creator_from_rss_feed_openai_api/   # Podcast creation using RSS feeds and APIs
│   │   └── quiz_maker/                                 # Quiz Creation starting form a URL 
│   ├── Phidata/                                        # Projects built using Phidata framework
│   │   └── podcast_creator_from_url_ollama_coquiTTS/   # Local podcast creation using Phidata
│   └── README.md                                       # Root repository documentation
```
