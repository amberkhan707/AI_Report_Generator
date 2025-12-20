<img width="1913" height="783" alt="image" src="https://github.com/user-attachments/assets/41a54b03-49f5-4add-8a0f-8596a34741bb" />

<img width="1842" height="713" alt="image" src="https://github.com/user-attachments/assets/39a038e2-7d18-48a6-bc79-ae3e1c2ba6b5" />

<img width="1827" height="662" alt="image" src="https://github.com/user-attachments/assets/c1e5bebd-4a91-4d5e-8c6c-2490fdfa6a8d" />

# AI Report Generator

A simple Streamlit application that generates a structured, AI-written technical report or blog post and allows exporting the final output as a PDF.  
The app uses **LangGraph** for workflow orchestration and **Groq-hosted LLMs** for content generation.

---

## Features

- Topic-based technical report / blog generation
- Automatic section outlining using structured outputs
- Parallel expansion of each section
- Final editorial pass for clarity and flow
- PDF export of the generated report
- Clean and minimal Streamlit UI

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** – Web UI
- **LangChain** – LLM abstractions
- **LangGraph** – Multi-step graph-based workflow
- **Groq LLM** – Text generation
- **Pydantic** – Structured output validation
- **ReportLab** – PDF generation
- **python-dotenv** – Environment variable management

---

## Project Structure

```text
.
├── app.py                 # Main Streamlit application
├── .env                   # Environment variables (not committed)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Installation

Clone the repository
```
git clone https://github.com/your-username/ai-report-generator.git
cd ai-report-generator
```

Create and activate a virtual environment
```
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

Install dependencies
```
pip install -r requirements.txt
```
Environment Setup

Create a .env file in the project root:
```
groq_api_key=YOUR_GROQ_API_KEY
```
Running the Application
```
streamlit run app.py
```

The application will open in your browser.

### How It Works

Input Topic
The user provides a blog or report topic.

Section Generation
The LLM generates a structured outline using a predefined schema.

Section Expansion
Each section is expanded into detailed content (150–300 words).

Report Assembly
All sections are merged into a single document.

Final Editing
The complete report is refined for clarity and coherence.

PDF Export
The final content can be downloaded as a PDF.

### Notes

The app does not store user data.

Output quality depends on the selected LLM and prompt configuration.

PDF formatting is basic and focuses on readability.
