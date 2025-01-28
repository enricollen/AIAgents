# 📰 News Processing and Reporting Pipeline

This project serves as the Hello World of CrewAI, emphasizing the use of a Custom Tool to showcase a simple yet effective news processing pipeline. It highlights how to parse news articles **from an RSS feed**, process the content, and generate a structured report. 

By leveraging the CrewAI framework, it demonstrates how to seamlessly integrate and orchestrate modular agents and tasks with custom tools, making it an ideal starting point for understanding and building more advanced CrewAI projects.

---

## 🧩 Components

### 1. **Agents**
- **News Parser Agent:**
  - Role: Extract and parse news articles from the RSS feed.
  - Tools: Utilizes the `NewsParserTool` custom tool for news parsing.
  - Config File: `config/tasks.yaml`
  
- **Reporting Analyst Agent:**
  - Role: Generate a detailed report based on the parsed news content.
  - Skills: Structured analysis and writing capabilities.
  - Config File: `config/tasks.yaml`

### 2. **Tasks**
- **Fetch News Task:**
  - Description: Parse the RSS feed and clean the extracted news articles.
  - Config File: `config/tasks.yaml`
  
- **Reporting Task:**
  - Description: Analyze the parsed news and create a structured report.
  - Config File: `config/tasks.yaml`
  - Output File: `src/news_reporting/outputs/report.md`

---

## 📂 Project Structure

```plaintext
.
├── src/
│   └── news_reporting/
|      ├── config/
│      |   └── agents.yaml              # Agent configurations
│      |   └── tasks.yaml               # Task configurations
│      ├── tools/
│      │   └── news_parser_tool.py      # Tool for parsing RSS feed
│      ├── outputs/
│      │   └── report.md                # Generated report
│      ├── crew.py                      # Crew definition
│      └── main.py                      # Main script to run the crew
│                        
├── .env                              # Environment variables
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
```
---
## 🚀 How to Run
1. **Clone the repository**:
   ```bash
   git clone https://github.com/enricollen/AIAgents
   cd crewAI/news_reporting
   ```
2. Create a .env file in the project root path (see .env_example for reference) and configure environment variables:
   ```plaintext
   OPENAI_API_KEY=YOUR_KEY_HERE
   MODEL=gpt-3.5-turbo
   RSS_FEED_URL=YOUR_RSS_URL_HERE 
   HOW_MANY_NEWS_TO_FETCH=1
   HOW_MANY_PARAGRAPHS_TO_FETCH=13
   ```
3. Run by using the CrewAI command:
   ```bash
   cd src/news_reporting
   crewai run
   ```

