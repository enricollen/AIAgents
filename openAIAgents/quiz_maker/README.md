# 📝 Quiz Maker with OpenAI Agent SDK

This project provides an automated pipeline to generate structured educational quizzes from **PDF files** and **web URLs**, using the **OpenAI Agent SDK**.

It combines:
- Text extraction (from PDFs or URLs)
- Summarization of educational content
- Generation of multiple-choice questions with structured scoring

The system supports both a **Streamlit-based interface** and **agent-based processing**.

---

## 🧠 How It Works

### 🔹 Input
- Upload one or more **PDF documents**, or
- Paste a list of **web URLs**

### 🔹 Processing Pipeline
1. **Extract Text**  
   - From PDFs using `PyPDFLoader`  
   - From URLs using `WebBaseLoader` + `Html2TextTransformer`
   
2. **Summarize Content**  
   - An agent (`text summarizer`) extracts and organizes key concepts

3. **Generate Quiz**  
   - An agent (`quiz generator`) creates 10 multiple-choice questions:
     - One correct answer (5 points)
     - One partially correct answer (2 points)
     - One incorrect answer (0 points)
     - One misleading or harmful answer (-2 points)

4. **Save Results**  
   - Quizzes are saved in structured JSON format  
   - Summaries and raw text are stored in dedicated folders

---

## 📂 Project Structure

```plaintext
quiz_maker/
├── raw_text/
│   └── *.txt (extracted original content)
├── summarized_text/
│   └── *_summary.txt (agent-generated summaries)
├── json_question_answers/
│   └── *_quiz.json (final quizzes in JSON format)
├── excel_question_answers/
│   └── *.xlsx (Excel format quizzes)
├── main.py (main application file)
├── excel_converter.py (Excel conversion utilities)
├── utils.py (utility functions)
├── ai_agent.py (AI agent implementation)
├── models.py (data models)
├── requirements.txt (dependencies)
├── .env_example (environment variables template)
└── README.md
```
---

## 💡 JSON Output Format

Each quiz is saved with this structure:

```json
{
  "questions": [
    {
      "theme": "question theme",
      "question_text": "Question text?",
      "answers": [
        { "text": "Correct answer", "score": 5 },
        { "text": "Partially correct answer", "score": 2 },
        { "text": "Incorrect answer", "score": 0 },
        { "text": "Misleading answer", "score": -2 }
      ]
    }
  ]
}
```

---
## 📺 App UI

Here's a screenshot of the Streamlit interface:
![AppUI](https://github.com/enricollen/AIAgents/blob/main/openAIAgents/quiz_maker/img/streamlit_ui_1.jpg?raw=true)

---

## 🚀 How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/enricollen/AIAgents
   cd openAIAgents/quiz_maker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/MacOS
   venv\Scripts\activate      # On Windows
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Rename the `.env_example` file in the project root and set your OpenAI key:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Run the application**:
   ```bash
   streamlit run main.py
   ```
