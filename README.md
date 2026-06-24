# AMAZEBOT

## What is AMAZEBOT?

AMAZEBOT is an advanced AI-powered application that combines document analysis, video processing, and engineering design assistance. It's built to help you interact with your content - whether it's documents, videos, or design problems - through intelligent conversation and analysis.

The application uses RAG (Retrieval-Augmented Generation) to understand the context of your uploaded files and answer questions accurately. It also includes specialized tools for design engineering, video analysis, and automated quiz generation.

---

## Main Features

**Document Processing**
- Upload and analyze PDFs, PowerPoint presentations, images, and text files
- Ask questions about your documents and get intelligent answers
- The system reads and understands the content, then provides relevant responses

**YouTube Video Analysis**
- Load YouTube videos by URL
- Ask questions about video content
- Generate summaries and key points
- Create quizzes from video content
- Extract important information and topics

**Design Engineering Assistant**
- Get help with engineering design problems across multiple domains:
  - Mechanical Engineering
  - Electrical Engineering
  - Civil/Structural Engineering
  - Software Architecture
  - Product Design
  - AI Systems Design
  - Electronics
  - Biomedical Engineering

**Smart Features**
- Automatic quiz generation from uploaded content
- Chat-based interface for natural conversation
- Export conversations and generated content
- Multi-document analysis and comparison
- Real-time processing and responses

---

## How It Works

1. **Upload Content**: Add a document, video link, or describe a design problem
2. **Process**: The application analyzes and understands your content
3. **Ask Questions**: Type natural questions about your content
4. **Get Answers**: Receive intelligent, context-aware responses
5. **Export**: Save your conversations and generated content

The application doesn't just search for keywords - it actually understands the meaning and context of your content, so you get accurate, relevant answers.

---

## Technology Stack

**Frontend**
- HTML5 with semantic markup
- CSS3 with modern design system
- Vanilla JavaScript (no dependencies)
- Dark mode optimized interface

**Backend**
- Python 3.8+
- Flask for web server
- RAG pipeline for document understanding

**AI & APIs**
- Anthropic Claude API for language understanding
- Google Gemini API for additional processing
- Vector embeddings for semantic search

**Libraries**
- python-dotenv for configuration
- requests for API communication
- Document processing libraries for PDF/PowerPoint handling

---

## What You Need

1. Python 3.8 or higher
   Download from https://python.org

2. API Keys (free to get)
   - Anthropic Claude: https://console.anthropic.com/
   - Google Gemini: https://ai.google.dev/

3. Git (optional but recommended)
   Download from https://git-scm.com

---

## Installation

**Windows:**
1. Extract the project folder
2. Create a `.env` file in the project folder
3. Add your API keys:
   ```
   ANTHROPIC_API_KEY=your-key-here
   GOOGLE_API_KEY=your-key-here
   ```
4. Double-click `START_WINDOWS.bat`
5. Open http://localhost:5000 in your browser

**Mac/Linux:**
```bash
git clone https://github.com/yourusername/AMAZEBOT.git
cd AMAZEBOT
python3 -m venv venv
source venv/bin/activate

# Create .env file and add your API keys
echo "ANTHROPIC_API_KEY=your-key" > .env
echo "GOOGLE_API_KEY=your-key" >> .env

pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

---

## Using AMAZEBOT

**For Document Analysis:**
1. Click upload and select your file
2. Wait for processing
3. Ask questions about the content
4. Get instant answers

Example questions:
- "What are the main points in this document?"
- "Summarize the key findings"
- "What does section 3 discuss?"

**For Video Analysis:**
1. Paste a YouTube URL
2. Click "Load Video"
3. Ask questions about the video
4. Get analysis and summaries

Example questions:
- "What's the main topic of this video?"
- "Summarize the key points"
- "Create a quiz from this video"

**For Design Help:**
1. Click the Design Engineering option
2. Select your engineering domain
3. Describe your design problem or idea
4. Get detailed engineering solutions

Example problems:
- "Design a solar-powered water filter for rural areas"
- "Design an AI-based attendance system for colleges"
- "Create a load-bearing bridge design for 20m span"

**Generate Quizzes:**
- Click Quiz option
- The app creates questions from your content
- Answer and get your score

---

## Architecture

```
Browser (HTML/CSS/JS)
    ↓
Flask Server (Python backend)
    ↓
    ├─ Document Processing
    ├─ Video Analysis
    ├─ RAG Pipeline
    └─ Design Engineering AI
    ↓
API Services
    ├─ Anthropic Claude
    └─ Google Gemini
```

**How RAG Works:**
1. Your document is uploaded
2. Text is extracted and broken into chunks
3. Semantic embeddings are created
4. When you ask a question, relevant sections are found
5. The AI reads these sections and answers your question

This ensures answers are based on your actual content, not just general knowledge.

---

## API Endpoints

| Endpoint | Method | What it does |
|----------|--------|------------|
| `/` | GET | Open the main page |
| `/api/upload` | POST | Upload a document |
| `/api/chat` | POST | Send a message, get response |
| `/api/youtube` | POST | Load a YouTube video |
| `/api/design` | POST | Generate design solutions |
| `/api/quiz` | POST | Generate quiz questions |
| `/api/export` | GET | Download conversation |

---

## Privacy & Security

Your information is protected:
- API keys stay on your computer only
- Documents are not permanently stored
- Video URLs are not saved
- No tracking or logging of your activity
- All processing happens securely

Best practices:
- Don't share your API keys with anyone
- Keep your `.env` file private
- Don't commit `.env` to version control

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
```bash
pip install -r requirements.txt
```

**"API key not found"**
- Check that `.env` file exists in the project folder
- Verify the format: `ANTHROPIC_API_KEY=sk-ant-api03-...`
- Restart the application

**"Connection refused"**
- Make sure the application is running
- Try: `python app.py`
- Check that port 5000 is not in use

**"Upload not working"**
- Check browser console (F12 → Console)
- Verify file format is supported
- Check file size (keep under 50MB)

**"YouTube video won't load"**
- Verify the URL is a valid YouTube link
- Check your internet connection
- Try a different video

---

## File Support

Supported formats:
- PDF files (up to 100 pages)
- PowerPoint presentations (up to 50 slides)
- Images (JPG, PNG, up to 20MB)
- Text files (up to 50MB)
- YouTube videos (via URL)

---

## Performance

- Document processing: Usually 5-15 seconds
- Response generation: 2-5 seconds depending on content
- Quiz generation: 10-20 seconds for comprehensive quizzes
- Design solutions: 15-30 seconds for detailed designs

---

## Deployment

You can deploy AMAZEBOT to the cloud:

**Heroku:**
```bash
heroku login
heroku create amazebot
git push heroku main
```

**Render or Replit:**
- Connect your GitHub repository
- Set environment variables
- Deploy with one click

---

## Project Status

- Complete document RAG chatbot
- YouTube video integration
- Design engineering assistant
- Quiz generation system
- Modern UI with dark mode
- API integration complete
- Ready for deployment

---

## About This Project

AMAZEBOT was created to explore how modern AI can be used for practical applications. It combines several cutting-edge technologies:
- Retrieval-Augmented Generation (RAG)
- Multi-modal content processing
- Real-time API integration
- Intelligent design assistance

The project demonstrates how AI can be integrated into everyday tools to make learning, analysis, and problem-solving more efficient and accessible.
