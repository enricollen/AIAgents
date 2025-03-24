# 📝 Quiz Maker with CrewAI

This project demonstrates an automated quiz creation pipeline that:
- Scrapes content from a website
- Processes and organizes the content into topics
- Creates multiple-choice questions

The application automates the entire workflow of transforming web content into structured quizzes (questions + answers). It leverages the modular design of agents and tasks, orchestrated by the **CrewAI framework**.

---

## 🧩 Components and Interactions

### 👥 Quiz Creation Crew
This crew handles the entire pipeline from web scraping to quiz generation.

#### **Agents**
- **Web Content Analyzer:** 
  - Role: Extract and analyze content from web pages
  - Tools: Uses `ScrapeWebsiteTool` for web scraping
  - Output: Raw content in Italian

- **Content Cleaner:** 
  - Role: Clean and filter web content
  - Output: Cleaned text without HTML or irrelevant elements

- **Content Organizer:**
  - Role: Structure content into distinct topics
  - Output: Organized content with numbered topics

- **Topics Divider:**
  - Role: Split content into separate topic files
  - Tools: Uses `TopicsDivider` custom tool
  - Output: Individual text files for each topic

- **Quiz Creator:**
  - Role: Generate multiple-choice questions
  - Tools: Uses `TxtToQuestionsTool` custom tool
  - Output: JSON files with questions and answers

#### **Tasks**
1. **Analyze Webpage:**
   - Description: Extract content from the specified URL
   - Output: Raw webpage content in Italian

2. **Clean Web Content:**
   - Description: Remove non-content elements and format text
   - Output: Clean, meaningful text

3. **Organize Content:**
   - Description: Structure content into numbered topics
   - Output: Text file with organized topics

4. **Divide Topics:**
   - Description: Create separate files for each topic
   - Output: Individual topic files

5. **Create Quiz Questions:**
   - Description: Generate multiple-choice questions for each topic
   - Output: JSON files with questions and answers

---

## 🛠️ How It Works

### Step 1: Content Extraction
- User provides a URL containing educational content
- Web Content Analyzer extracts the content
- Content Cleaner removes HTML and irrelevant elements

### Step 2: Content Organization
- Content Organizer structures the text into topics
- Topics Divider creates separate files for each topic

### Step 3: Quiz Generation
- Quiz Creator generates multiple-choice questions for each topic
- Each question has 4 possible answers

### Step 5: Save Results
- Questions are saved as JSON files in the `output/questions` directory

---

## 📁 Project Structure
```plaintext
crewAI/quiz_maker/
├── src/
│ └── quiz_maker/
│ ├── tools/
│ │ ├── answers_scorer.py
│ │ ├── divide_topics_into_txt.py
│ │ └── txt_to_questions.py
│ ├── config/
│ │ ├── agents.yaml
│ │ └── tasks.yaml
│ ├── crew.py
│ └── main.py
├── output/
│ ├── original_content.txt
│ ├── divided_topics/
│ │ └── topic_1.txt
| | └── topic_2.txt
| | └── topic_3.txt
| | └── ...
| ├── questions/
│   └── questions_topic_1.json
|   └── questions_topic_2.json
|   └── questions_topic_3.json
|   └── ...
│ 
└── README.md
```

---

## 🚀 How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/quiz-maker
   cd crewAI/quiz_maker
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
   Create a `.env` file in the project root:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Run the application**:
   ```bash
   crewai run
   ```

The application will process the content and generate:
- Organized topic files
- Multiple-choice questions for each different topic in the web page

---

## 📝 Output Format

### Questions JSON Format
```json
{
"topic": "1",
"content": "Topic content...",
"questions": [
{
"question": "Question text?",
"options": {
"A": "First option",
"B": "Second option",
"C": "Third option",
"D": "Fourth option"
},
"correct_answer": "A"
}
]
}
```
