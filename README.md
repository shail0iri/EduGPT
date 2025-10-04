# 🎓 EduGPT - Your AI Instructor with MCP Tools

EduGPT is an advanced AI-powered educational platform that creates personalized course syllabi and provides interactive teaching using Google Gemini AI and MCP (Model Context Protocol) tools.

## ✨ Features

- 🤖 **AI-Powered Syllabus Generation**: Create comprehensive course outlines automatically
- 👨‍🏫 **Interactive AI Instructor**: Personalized, adaptive teaching sessions
- 🛠️ **MCP Tools Integration**: Real-time Wikipedia research, file system access, and more
- 🎯 **Multi-Subject Support**: From programming to humanities
- 💬 **Web Interface**: User-friendly Gradio interface
- 🔧 **Extensible Architecture**: Easy to add new tools and features

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+ (for MCP tools)
- pip package manager
- Google Gemini API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/EduGPT.git
   cd EduGPT


2. **Install Dependencies**:
    '''bash
       pip install -r requirements.txt

3. **Set up env**:
   '''bash
   cp .env.example .env
   # Edit .env with your API keys and configuration

4. **Run the Application**:
    '''bash
      python app.py

Usage
Web Interface
Access the web interface at http://localhost:5000 after starting the application.

API Endpoints
POST /api/chat - Send messages to EduGPT

GET /api/subjects - Get available subjects

POST /api/assessment - Create personalized assessments

