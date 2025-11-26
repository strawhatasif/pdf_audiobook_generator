# 📚 PDF to Audiobook Converter

A web-based application that converts PDF documents into audiobooks using Google Text-to-Speech (gTTS).

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Multiple Accents**: Choose from US, UK, Australian, Indian, Canadian English and other languages
- **Automatic Chapter Detection**: Intelligently splits PDFs by chapter headings
- **Web Interface**: Clean, modern UI that runs locally in your browser
- **Batch Download**: Download all chapters as a single ZIP file
- **Reliable**: Uses Google's stable TTS service

## 🖥️ Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  📚 PDF to Audiobook Converter                              │
├─────────────────────────────────────────────────────────────┤
│  📄 Upload & Settings          │  📊 Output                 │
│  ┌─────────────────────────┐   │  ┌─────────────────────┐   │
│  │  📎 Drop PDF here       │   │  │ ✅ Chapter 1: Intro │   │
│  └─────────────────────────┘   │  │ ✅ Chapter 2: ...   │   │
│  🎙️ Voice: [English (US) ▼]   │  │ ✅ Chapter 3: ...   │   │
│  [🎧 Convert to Audiobook]     │  └─────────────────────┘   │
│                                │  [📥 Download ZIP]         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 - 3.12** (3.13+ not yet supported due to dependency compatibility)
- Internet connection (required for text-to-speech)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/strawhatasif/pdf_audiobook_generator.git
   cd pdf_audiobook_generator
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   # Create venv
   python -m venv venv
   
   # Activate (Windows GitBash)
   source venv/Scripts/activate
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```

4. **Open your browser** to `http://127.0.0.1:7860`

### Usage

1. Upload a PDF file
2. Select a voice/accent from the dropdown
3. Click "Convert to Audiobook"
4. Download the ZIP file with all chapter audio files

### Alternative: Using run.sh

You can also use the included launch script:

```bash
# GitBash (Windows), macOS, or Linux
./run.sh
```

The script will:
- Create a virtual environment (first run only)
- Install all dependencies (first run only)
- Launch the app

## 🔧 Troubleshooting

### Python version issues
If you see errors about missing wheels or failed builds:
- **Use Python 3.10, 3.11, or 3.12** (not 3.13 or 3.14)
- Check version: `python --version`
- Download Python 3.12: https://www.python.org/downloads/release/python-3129/

### Gradio/localhost issues
If you get errors about localhost not being accessible:
- The app clears proxy settings automatically
- If still failing, try: `app.launch(share=True)` in app.py

### Pillow build errors
```bash
pip install --only-binary=:all: Pillow
```

## 🎙️ Available Voices

| Voice | Language | Accent |
|-------|----------|--------|
| English (US) | English | American |
| English (UK) | English | British |
| English (Australia) | English | Australian |
| English (India) | English | Indian |
| English (Canada) | English | Canadian |
| Spanish | Spanish | Standard |
| French | French | Standard |
| German | German | Standard |
| Italian | Italian | Standard |
| Portuguese | Portuguese | Standard |

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
# Add more voices/languages
VOICE_OPTIONS = {
    "Display Name": {"lang": "en", "tld": "com"},
    ...
}

# Change pages per chapter for auto-splitting
pages_per_chunk = 10  # in detect_chapters()

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

- [gTTS](https://github.com/pndurette/gTTS) - Google Text-to-Speech library
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF text extraction
- [Gradio](https://gradio.app/) - Web interface framework

## ⚠️ Disclaimer

This tool uses Google's text-to-speech service. Please review Google's terms of service regarding usage. This project is intended for personal use.
