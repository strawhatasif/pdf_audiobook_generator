"""
PDF to Audiobook Converter
Converts PDF files to MP3 audiobooks using Google Text-to-Speech (gTTS)
"""

import os
import re
import tempfile
import zipfile
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message=".*gradio version.*")
warnings.filterwarnings("ignore", message=".*please upgrade.*")

# Clear proxy settings that might interfere with localhost
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

import gradio as gr
import pdfplumber
from gtts import gTTS

# Available languages/accents for gTTS
VOICE_OPTIONS = {
    "English (US)": {"lang": "en", "tld": "com"},
    "English (UK)": {"lang": "en", "tld": "co.uk"},
    "English (Australia)": {"lang": "en", "tld": "com.au"},
    "English (India)": {"lang": "en", "tld": "co.in"},
    "English (Canada)": {"lang": "en", "tld": "ca"},
    "Spanish": {"lang": "es", "tld": "com"},
    "French": {"lang": "fr", "tld": "com"},
    "German": {"lang": "de", "tld": "com"},
    "Italian": {"lang": "it", "tld": "com"},
    "Portuguese": {"lang": "pt", "tld": "com"},
}


def extract_text_from_pdf(pdf_path: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Extract text from PDF and attempt to detect chapters.
    Returns: (full_text, list of (chapter_title, chapter_text))
    """
    full_text = ""
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
            full_text += text + "\n\n"

    # Try to detect chapters
    chapters = detect_chapters(full_text, pages_text)

    return full_text, chapters


def detect_chapters(full_text: str, pages_text: list[str]) -> list[tuple[str, str]]:
    """
    Detect chapter boundaries in the text.
    Returns list of (chapter_title, chapter_text) tuples.
    """
    # Common chapter patterns
    chapter_patterns = [
        r'^(Chapter\s+\d+[:\s].{0,100})$',
        r'^(CHAPTER\s+\d+[:\s].{0,100})$',
        r'^(Part\s+\d+[:\s].{0,100})$',
        r'^(PART\s+\d+[:\s].{0,100})$',
        r'^(Section\s+\d+[:\s].{0,100})$',
        r'^(\d+\.\s+[A-Z].{0,100})$',
    ]

    combined_pattern = '|'.join(f'({p})' for p in chapter_patterns)

    chapters = []
    lines = full_text.split('\n')

    current_chapter_title = "Introduction"
    current_chapter_lines = []
    chapter_starts = []

    # Find all chapter headings (excluding TOC entries)
    toc_pattern = re.compile(r'^\s*(chapter|part|section)\s+\d+.*\d+\s*$', re.IGNORECASE)

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Skip TOC entries (lines ending with page numbers)
        if toc_pattern.match(line_stripped):
            continue

        for pattern in chapter_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                chapter_starts.append((i, line_stripped))
                break

    # If we found chapters, split the text
    if chapter_starts:
        for idx, (line_num, title) in enumerate(chapter_starts):
            # Get end line (start of next chapter or end of document)
            if idx + 1 < len(chapter_starts):
                end_line = chapter_starts[idx + 1][0]
            else:
                end_line = len(lines)

            chapter_text = '\n'.join(lines[line_num:end_line])

            # Only add if chapter has substantial content
            if len(chapter_text.strip()) > 100:
                chapters.append((title[:50], chapter_text))

    # If no chapters found or chapters are too large, split by pages
    if not chapters or (len(chapters) == 1 and len(chapters[0][1]) > 50000):
        chapters = []
        pages_per_chunk = 10

        for i in range(0, len(pages_text), pages_per_chunk):
            chunk_pages = pages_text[i:i + pages_per_chunk]
            chunk_text = '\n\n'.join(chunk_pages)

            if chunk_text.strip():
                part_num = (i // pages_per_chunk) + 1
                chapters.append((f"Part {part_num}", chunk_text))

    # Final fallback: treat entire document as one chapter
    if not chapters:
        chapters = [("Full Document", full_text)]

    return chapters


def clean_text_for_speech(text: str) -> str:
    """Clean and prepare text for TTS conversion."""
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Remove common PDF artifacts
    text = re.sub(r'\.{3,}', '...', text)

    # Ensure sentences end with proper punctuation for better TTS pacing
    text = re.sub(r'([a-z])\n([A-Z])', r'\1. \2', text)

    return text.strip()


def convert_pdf_to_audiobook(pdf_file, voice_name: str, progress=gr.Progress()):
    """
    Main conversion function.
    """
    if pdf_file is None:
        return None, "❌ Please upload a PDF file."

    # Handle different types of file inputs from Gradio
    if isinstance(pdf_file, str):
        pdf_path = pdf_file
    elif hasattr(pdf_file, 'name'):
        pdf_path = pdf_file.name
    else:
        pdf_path = str(pdf_file)

    # Get voice settings
    voice_settings = VOICE_OPTIONS.get(voice_name, VOICE_OPTIONS["English (US)"])

    # Create temp directory for output
    output_dir = tempfile.mkdtemp(prefix="audiobook_")

    status_messages = []
    status_messages.append(f"📁 PDF path: {pdf_path}")
    status_messages.append(f"🎙️ Voice: {voice_name}")
    status_messages.append(f"📂 Output dir: {output_dir}")

    try:
        # Extract text
        progress(0.1, desc="Extracting text from PDF...")
        full_text, chapters = extract_text_from_pdf(pdf_path)

        if not full_text.strip():
            return None, "❌ Could not extract text from PDF. The PDF may be scanned images (not text-based)."

        status_messages.append(f"📚 Found {len(chapters)} chapter(s)")
        for i, (title, text) in enumerate(chapters):
            status_messages.append(f"   Part {i+1}: {len(text)} chars - '{title[:30]}...'")

        audio_files = []

        # Convert each chapter
        for i, (chapter_title, chapter_text) in enumerate(chapters):
            progress((0.1 + 0.8 * i / len(chapters)), desc=f"Converting chapter {i+1}/{len(chapters)}...")

            # Clean text
            clean_text = clean_text_for_speech(chapter_text)

            if len(clean_text) < 10:
                status_messages.append(f"⚠️ Chapter {i+1} skipped (too short)")
                continue

            status_messages.append(f"   Cleaned text length: {len(clean_text)} chars")

            # Generate safe filename
            safe_title = re.sub(r'[^\w\s-]', '', chapter_title)[:30].strip()
            safe_title = re.sub(r'\s+', '_', safe_title)
            output_filename = f"{i+1:02d}_{safe_title}.mp3"
            output_path = os.path.join(output_dir, output_filename)

            status_messages.append(f"   Converting to: {output_filename}")

            try:
                # Use gTTS for conversion
                tts = gTTS(
                    text=clean_text,
                    lang=voice_settings["lang"],
                    tld=voice_settings["tld"],
                    slow=False
                )
                tts.save(output_path)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    audio_files.append(output_path)
                    status_messages.append(f"✅ Chapter {i+1} converted successfully")
                else:
                    status_messages.append(f"❌ Chapter {i+1} failed - empty output")

            except Exception as e:
                status_messages.append(f"❌ Chapter {i+1} TTS failed: {str(e)}")
                continue

        if not audio_files:
            return None, "❌ No audio files were generated.\n\n" + "\n".join(status_messages)

        # Create ZIP file with all audio
        progress(0.95, desc="Creating ZIP file...")
        zip_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_audiobook.zip"
        zip_path = os.path.join(output_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for audio_file in audio_files:
                zipf.write(audio_file, os.path.basename(audio_file))

        progress(1.0, desc="Complete!")

        status_messages.append(f"\n✅ Successfully created {len(audio_files)} audio file(s)")
        status_messages.append(f"📦 ZIP file: {zip_filename}")

        return zip_path, "\n".join(status_messages)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        status_messages.append(f"\n❌ Error: {str(e)}")
        status_messages.append(f"\nFull traceback:\n{error_details}")
        return None, "\n".join(status_messages)


# Build Gradio interface
with gr.Blocks(title="PDF to Audiobook Converter") as app:
    gr.Markdown("""
    # 📚 PDF to Audiobook Converter
    
    Convert your PDF documents into MP3 audiobooks using Google Text-to-Speech.
    
    **Features:**
    - Automatic chapter detection
    - Multiple voice accents available
    - Downloads as ZIP file with all chapters
    """)

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath"
            )

            voice_dropdown = gr.Dropdown(
                choices=list(VOICE_OPTIONS.keys()),
                value="English (US)",
                label="Voice/Accent"
            )

            convert_btn = gr.Button("🎧 Convert to Audiobook", variant="primary")

        with gr.Column(scale=1):
            output_file = gr.File(label="Download Audiobook (ZIP)")
            status_output = gr.Textbox(
                label="Status",
                lines=15,
                max_lines=25
            )

    convert_btn.click(
        fn=convert_pdf_to_audiobook,
        inputs=[pdf_input, voice_dropdown],
        outputs=[output_file, status_output]
    )

    gr.Markdown("""
    ---
    **Notes:**
    - Works best with text-based PDFs (not scanned images)
    - Large PDFs are automatically split into parts
    - Requires internet connection for TTS
    """)


if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)
