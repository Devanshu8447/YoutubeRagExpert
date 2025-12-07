# YouTube RAG Expert 

A powerful Retrieval-Augmented Generation (RAG) application that transforms YouTube videos into interactive learning experiences. Extract transcripts, generate comprehensive study notes, ask intelligent questions, and download everything as PDF - all from a single YouTube URL.

**Key Capabilities:**
- 📝 **Auto-generate structured notes** from any YouTube video
- 📥 **Download notes as PDF** for offline study and reference
- 💬 **Ask questions** and get accurate, AI-powered answers from video content
- 🎯 **RAG-powered intelligence** for context-aware responses

## 🌟 Features

- **YouTube Transcript Extraction**: Automatically fetches and processes transcripts from YouTube videos
- **Intelligent Q&A**: Ask questions about video content and get accurate, context-aware answers
- **Auto-Generated Notes**: Automatically generate comprehensive, structured notes from video content
- **Downloadable Notes**: Export generated notes in various formats for offline access and study
- **RAG-Powered**: Leverages Retrieval-Augmented Generation for enhanced response quality
- **Docker Support**: Easy deployment with containerization
- **Web Interface**: User-friendly Streamlit interface for seamless interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- OpenAI API key or other LLM API credentials

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/Devanshu8447/YoutubeRagExpert.git
   cd YoutubeRagExpert
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
```env
   OPENAI_API_KEY=your_api_key_here
   # Add other required API keys
```

4. **Run the application**
```bash
   python app.py
```

### Docker Deployment

1. **Build the Docker image**
```bash
   docker build -t youtube-rag-expert .
```

2. **Run the container**
```bash
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_api_key youtube-rag-expert
```

3. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage

1. **Enter YouTube URL**: Paste the URL of the YouTube video you want to analyze
2. **Wait for Processing**: The application will extract and process the transcript
3. **Generate Notes**: Click the "Generate Notes" button to create comprehensive notes from the video
4. **Download Notes**: Export your notes in PDF, Markdown, or TXT format
5. **Ask Questions**: Type your questions about the video content
6. **Get Answers**: Receive AI-generated answers based on the video transcript

## 🏗️ Project Structure
```
YoutubeRagExpert/
├── app.py                      # Main application file
├── supporting_functions.py     # Helper functions and utilities
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## 🔧 Technologies Used

- **Python**: Core programming language
- **LangChain**: Framework for LLM application development
- **OpenAI/LLM APIs**: Language model integration
- **YouTube Transcript API**: Transcript extraction
- **Vector Databases**: For efficient document retrieval
- **Streamlit/Flask**: Web interface framework
- **Docker**: Containerization

## 📝 How It Works

1. **Transcript Extraction**: The application fetches the transcript from YouTube videos using the YouTube Transcript API
2. **Text Processing**: Transcripts are chunked and processed for optimal retrieval
3. **Vector Embedding**: Text chunks are converted into vector embeddings
4. **Storage**: Embeddings are stored in a vector database for efficient retrieval
5. **Notes Generation**: AI analyzes the content and generates structured, comprehensive notes
6. **Query Processing**: User questions are embedded and matched against stored vectors
7. **Answer Generation**: Retrieved context is used to generate accurate answers using LLMs
8. **Export**: Notes and summaries can be exported in multiple formats including PDF

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Known Issues

- Some YouTube videos may not have available transcripts
- Processing very long videos may take additional time
- API rate limits may apply depending on your LLM provider

## 🔮 Future Enhancements

- [ ] Support for multiple languages
- [ ] Batch processing of multiple videos
- [ ] Export Q&A sessions
- [ ] Multiple note formats (Word, HTML)
- [ ] Custom note templates
- [ ] Enhanced caching mechanisms
- [ ] Support for video playlists
- [ ] Integration with more LLM providers
- [ ] Note sharing and collaboration features

## 📧 Contact

**Devanshu** - [@Devanshu8447](https://github.com/Devanshu8447)

Project Link: [https://github.com/Devanshu8447/YoutubeRagExpert](https://github.com/Devanshu8447/YoutubeRagExpert)

## 🙏 Acknowledgments

- LangChain for the RAG framework
- YouTube Transcript API contributors
- The open-source community

---

⭐ If you find this project useful, please consider giving it a star!
