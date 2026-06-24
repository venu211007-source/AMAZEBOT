# AMAZEBOT

## About This Project

AMAZEBOT is a document-based chatbot application that uses Retrieval-Augmented Generation (RAG) to help users interact with their documents. The main idea is to make it easy for anyone to upload documents and ask questions about them without worrying about data privacy.

What it does:
- Upload documents in different formats (PDF, PowerPoint, images, text files)
- Ask questions about the content of uploaded documents
- Get answers based on the actual document content
- Generate quizzes automatically from the documents
- Export conversations for later reference

The application keeps everything private - your documents are not stored on any server, and your API key stays on your machine.

---

## Features

- Document Upload: Supports PDF, PPTX, images, and text files
- Smart Q&A: Ask questions and get answers based on your documents
- Quiz Generation: Automatically creates questions from document content
- Privacy: Your documents are processed locally and not stored
- Simple to Use: Clean interface that's easy to navigate
- Export Feature: Save your conversations for future reference

---

## Technology Used

Backend:
- Python 3.8 or higher
- Flask for the web server
- Anthropic Claude API for AI capabilities

Frontend:
- HTML5 for structure
- CSS3 for styling
- JavaScript for interactivity

Other Libraries:
- python-dotenv for managing environment variables
- requests for making HTTP calls

---

## What You Need Before Starting

1. Python 3.8 or higher installed on your computer
   Go to https://python.org to download it

2. An Anthropic API key
   You can get this free from https://console.anthropic.com/
   
3. Git installed (optional but recommended)
   Download from https://git-scm.com

---

## How to Set Up and Run

On Windows:
1. Extract the project folder to your computer
2. Create a file named `.env` in the project folder
3. Open the `.env` file and add your API key like this:
   ANTHROPIC_API_KEY=your-actual-api-key-here
4. Double-click the file named START_WINDOWS.bat
5. Open your web browser and go to http://localhost:5000

On Mac or Linux:
1. Open terminal in the project folder
2. Run these commands:
   
   python3 -m venv venv
   source venv/bin/activate
   
   Create a .env file and add your API key:
   echo "ANTHROPIC_API_KEY=your-api-key" > .env
   
   Then install and run:
   pip install -r requirements.txt
   python app.py

3. Open http://localhost:5000 in your browser

---

## Using AMAZEBOT

Basic steps:
1. Click on the upload button and select a document
2. Wait for the document to be processed
3. Type your question in the chat box
4. The application will answer based on the document content
5. You can ask multiple questions about the same document
6. To generate a quiz, click the quiz button and answer the questions
7. You can export your entire conversation if needed

---

## How It Works

The application follows this flow:
1. You upload a document through the web interface
2. The text is extracted from your document
3. When you ask a question, it finds the most relevant parts of the document
4. It sends this information to the Claude AI
5. Claude generates an answer based on the document content
6. Your answer appears in the chat

All of this happens quickly and your document content stays on your computer.

---

## API Details

The application has these main endpoints:
- GET / - Opens the main page
- POST /api/chat - Sends your question and gets answers
- POST /api/upload - Uploads a document
- POST /api/quiz - Generates a quiz from the document

---

## Important Security Information

Your privacy is protected:
- Your API key is only stored on your computer, not on any server
- Documents are not saved or stored anywhere permanent
- Text extraction for Office files happens in your browser
- We do not track or log your activity
- All processing either happens locally or goes directly to Anthropic

Best practices:
- Do not share your API key with anyone
- Keep your .env file secret
- Do not commit the .env file to version control

---

## Common Issues and Solutions

If you see "ModuleNotFoundError: No module named 'flask'"
Run this command:
pip install -r requirements.txt

If you see "ANTHROPIC_API_KEY not found"
Make sure you created the .env file in the right folder
The format should be: ANTHROPIC_API_KEY=sk-ant-api03-...

If you get "Connection refused" errors
Make sure the application is running
You can start it with: python app.py

If the API key is invalid
Get a new one from https://console.anthropic.com/
Update your .env file and restart the application

---

## License

This project is released under the MIT License. You can find the full license terms in the LICENSE file.

---

## About This Project

This is a student project developed to explore how RAG systems work and to create a practical application that demonstrates the concepts learned. The project focuses on combining document processing with modern AI capabilities in a way that's useful for everyday tasks like studying or document analysis.
