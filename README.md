# 📚 PDF to Audiobook Converter

A web-based application that converts PDF documents into high-quality audiobooks using Microsoft Edge's text-to-speech technology.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **High-Quality Voices**: Natural-sounding narration using Microsoft Edge TTS (100+ voices available)
- **Automatic Chapter Detection**: Intelligently splits PDFs by chapter headings
- **Multiple Voice Options**: Choose from US, UK, Australian, Indian English voices (male/female)
- **Adjustable Speed**: Control playback speed from 0.5x to 2.0x
- **Web Interface**: Clean, modern UI that runs locally in your browser
- **Batch Download**: Download all chapters as a single ZIP file

## 🖥️ Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  📚 PDF to Audiobook Converter                              │
├─────────────────────────────────────────────────────────────┤
│  📄 Upload & Settings          │  📊 Output                 │
│  ┌─────────────────────────┐   │  ┌─────────────────────┐   │
│  │  📎 Drop PDF here       │   │  │ ✅ Chapter 1: Intro │   │
│  └─────────────────────────┘   │  │ ✅ Chapter 2: ...   │   │
│  🎙️ Voice: [en-US-Aria ▼]     │  │ ✅ Chapter 3: ...   │   │
│  ⚡ Speed: [────●────] 1.0x   │  └─────────────────────┘   │
│  [🎧 Generate Audiobook]       │  [📥 Download ZIP]         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Internet connection (required for text-to-speech)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/strawhatasif/pdf_audiobook_generator.git
   cd pdf_audiobook_generator
   ```

2. **Run the app** (handles setup automatically)
   ```bash
   ./run.sh
   ```

That's it! The script creates a virtual environment and installs dependencies on first run.

### Usage

#### Quick Start (Recommended)
Simply run the included script - it handles everything automatically:

```bash
# GitBash (Windows), macOS, or Linux
./run.sh
```

The script will:
- Create a virtual environment (first run only)
- Install all dependencies (first run only)
- Launch the app and open your browser

#### Manual Start
If you prefer to run manually:

```bash
# Activate virtual environment
# Windows (GitBash):
source venv/Scripts/activate
# macOS/Linux:
source venv/bin/activate

# Run the app
python app.py
```

The app opens automatically at `http://127.0.0.1:7860`

3. **Convert your PDF**
   - Upload a PDF file
   - Select a voice
   - Adjust speed if desired
   - Click "Generate Audiobook"
   - Download the ZIP file with all chapters

## 🎙️ Available Voices

| Voice | Gender | Accent |
|-------|--------|--------|
| en-US-AriaNeural | Female | American |
| en-US-GuyNeural | Male | American |
| en-US-JennyNeural | Female | American |
| en-US-ChristopherNeural | Male | American |
| en-GB-SoniaNeural | Female | British |
| en-GB-RyanNeural | Male | British |
| en-AU-NatashaNeural | Female | Australian |
| en-AU-WilliamNeural | Male | Australian |
| en-IN-NeerjaNeural | Female | Indian |
| en-IN-PrabhatNeural | Male | Indian |

## 📖 How Chapter Detection Works

The application automatically detects chapters using common patterns:

- `Chapter 1`, `Chapter 2`, etc.
- `Chapter I`, `Chapter II`, etc. (Roman numerals)
- `Part 1`, `Part 2`, etc.
- `Section 1`, `Section 2`, etc.
- Numbered headings like `1. Introduction`

For PDFs without clear chapter markers, the content is split into ~10-page segments.

## 🔧 Configuration

You can modify the following in `app.py`:

```python
# Add more voices to the dropdown
POPULAR_VOICES = {
    "Display Name": "voice-id",
    ...
}

# Change pages per chapter for auto-splitting
pages_per_chapter = 10  # in split_by_pages()

# Modify the server settings
app.launch(
    server_name="127.0.0.1",  # Use "0.0.0.0" for network access
    server_port=7860,
    share=False,  # Set True for public URL
)
```

## 📁 Project Structure

```
pdf_audiobook_generator/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── run.sh              # Cross-platform launch script
├── README.md           # This file
├── LICENSE             # MIT License
└── test_installation.py # Installation verification
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [edge-tts](https://github.com/rany2/edge-tts) - Microsoft Edge TTS library
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF text extraction
- [Gradio](https://gradio.app/) - Web interface framework

## ⚠️ Disclaimer

This tool uses Microsoft Edge's online text-to-speech service. Please review Microsoft's terms of service regarding usage. This project is intended for personal use.
