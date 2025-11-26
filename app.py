"""
PDF to Audiobook Converter
A web-based application that converts PDF files to audiobooks using edge-tts.
"""

import asyncio
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Generator

import edge_tts
import gradio as gr
import pdfplumber


# ============================================================================
# Voice Configuration
# ============================================================================

# Popular English voices (subset for cleaner UI)
POPULAR_VOICES = {
    "en-US-AriaNeural (Female, US)": "en-US-AriaNeural",
    "en-US-GuyNeural (Male, US)": "en-US-GuyNeural",
    "en-US-JennyNeural (Female, US)": "en-US-JennyNeural",
    "en-US-ChristopherNeural (Male, US)": "en-US-ChristopherNeural",
    "en-GB-SoniaNeural (Female, UK)": "en-GB-SoniaNeural",
    "en-GB-RyanNeural (Male, UK)": "en-GB-RyanNeural",
    "en-AU-NatashaNeural (Female, AU)": "en-AU-NatashaNeural",
    "en-AU-WilliamNeural (Male, AU)": "en-AU-WilliamNeural",
    "en-IN-NeerjaNeural (Female, India)": "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural (Male, India)": "en-IN-PrabhatNeural",
}


# ============================================================================
# PDF Processing
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from PDF and attempt to detect chapters.
    
    Returns a list of dictionaries with 'title' and 'content' keys.
    """
    chapters = []
    current_chapter = {"title": "Chapter 1", "content": ""}
    chapter_count = 1
    
    # Common chapter heading patterns
    chapter_patterns = [
        r'^chapter\s+\d+',
        r'^chapter\s+[ivxlcdm]+',
        r'^\d+\.\s+[A-Z]',
        r'^part\s+\d+',
        r'^section\s+\d+',
    ]
    combined_pattern = re.compile('|'.join(chapter_patterns), re.IGNORECASE)
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            
            # Check for chapter headings in the text
            lines = text.split('\n')
            for line in lines:
                line_stripped = line.strip()
                
                # Check if this line looks like a chapter heading
                if combined_pattern.match(line_stripped) and len(line_stripped) < 100:
                    # Save current chapter if it has content
                    if current_chapter["content"].strip():
                        chapters.append(current_chapter)
                    
                    chapter_count += 1
                    current_chapter = {
                        "title": line_stripped[:50],  # Limit title length
                        "content": ""
                    }
                else:
                    current_chapter["content"] += line + "\n"
    
    # Don't forget the last chapter
    if current_chapter["content"].strip():
        chapters.append(current_chapter)
    
    # If no chapters detected, split by pages or create single chapter
    if len(chapters) == 0:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n\n"
            chapters = [{"title": "Full Document", "content": full_text}]
    
    # If only one chapter with lots of content, consider splitting by page count
    if len(chapters) == 1 and len(chapters[0]["content"]) > 50000:
        chapters = split_by_pages(pdf_path)
    
    return chapters


def split_by_pages(pdf_path: str, pages_per_chapter: int = 10) -> list[dict]:
    """
    Split PDF into chapters based on page count.
    """
    chapters = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        
        for start_page in range(0, total_pages, pages_per_chapter):
            end_page = min(start_page + pages_per_chapter, total_pages)
            
            content = ""
            for page_num in range(start_page, end_page):
                content += (pdf.pages[page_num].extract_text() or "") + "\n\n"
            
            chapter_num = (start_page // pages_per_chapter) + 1
            chapters.append({
                "title": f"Part {chapter_num} (Pages {start_page + 1}-{end_page})",
                "content": content
            })
    
    return chapters


def clean_text_for_speech(text: str) -> str:
    """
    Clean and prepare text for text-to-speech conversion.
    """
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove page numbers (common patterns)
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    
    # Remove headers/footers that repeat (basic heuristic)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip very short lines that are likely page numbers or artifacts
        if len(line.strip()) > 2 or line.strip() == '':
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Ensure proper sentence spacing for natural speech
    text = re.sub(r'\.(?=[A-Z])', '. ', text)
    
    return text.strip()


# ============================================================================
# Text-to-Speech Conversion
# ============================================================================

async def text_to_speech_async(
    text: str,
    output_path: str,
    voice: str = "en-US-AriaNeural",
    rate: str = "+0%",
    volume: str = "+0%"
) -> None:
    """
    Convert text to speech using edge-tts.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await communicate.save(output_path)


def text_to_speech(
    text: str,
    output_path: str,
    voice: str = "en-US-AriaNeural",
    rate: str = "+0%",
    volume: str = "+0%"
) -> None:
    """
    Synchronous wrapper for text-to-speech conversion.
    """
    asyncio.run(text_to_speech_async(text, output_path, voice, rate, volume))


# ============================================================================
# Main Conversion Pipeline
# ============================================================================

def convert_pdf_to_audiobook(
    pdf_file,
    voice_name: str,
    speed: float,
    progress: gr.Progress = gr.Progress()
) -> tuple[str, str, list]:
    """
    Main function to convert PDF to audiobook.
    
    Returns:
        - Status message
        - Path to zip file containing all audio files
        - List of individual audio file paths for preview
    """
    if pdf_file is None:
        return "❌ Please upload a PDF file.", None, []
    
    # Get the voice ID from the display name
    voice_id = POPULAR_VOICES.get(voice_name, "en-US-AriaNeural")
    
    # Convert speed to rate string
    rate_percent = int((speed - 1.0) * 100)
    rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
    
    # Create output directory
    output_dir = tempfile.mkdtemp(prefix="audiobook_")
    audio_files = []
    
    try:
        # Extract chapters from PDF
        progress(0.1, desc="📖 Extracting text from PDF...")
        chapters = extract_text_from_pdf(pdf_file.name)
        
        if not chapters:
            return "❌ Could not extract text from PDF.", None, []
        
        total_chapters = len(chapters)
        status_lines = [f"📚 Found {total_chapters} chapter(s)"]
        
        # Process each chapter
        for i, chapter in enumerate(chapters):
            progress_val = 0.1 + (0.8 * (i / total_chapters))
            progress(progress_val, desc=f"🎙️ Converting chapter {i+1}/{total_chapters}...")
            
            # Clean the text
            cleaned_text = clean_text_for_speech(chapter["content"])
            
            if not cleaned_text or len(cleaned_text) < 10:
                status_lines.append(f"⚠️ Chapter {i+1} skipped (no content)")
                continue
            
            # Generate safe filename
            safe_title = re.sub(r'[^\w\s-]', '', chapter["title"])[:30]
            safe_title = safe_title.strip().replace(' ', '_')
            output_filename = f"{i+1:02d}_{safe_title}.mp3"
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert to speech
            try:
                text_to_speech(cleaned_text, output_path, voice_id, rate)
                audio_files.append(output_path)
                status_lines.append(f"✅ Chapter {i+1}: {chapter['title'][:40]}")
            except Exception as e:
                status_lines.append(f"❌ Chapter {i+1} failed: {str(e)[:50]}")
        
        if not audio_files:
            return "❌ No audio files were generated.", None, []
        
        # Create zip file with all audio
        progress(0.95, desc="📦 Creating zip archive...")
        zip_path = os.path.join(output_dir, "audiobook.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for audio_file in audio_files:
                zipf.write(audio_file, os.path.basename(audio_file))
        
        progress(1.0, desc="✨ Complete!")
        
        status_message = "\n".join(status_lines)
        status_message += f"\n\n🎉 Successfully created {len(audio_files)} audio file(s)!"
        
        return status_message, zip_path, audio_files
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None, []


# ============================================================================
# Gradio Interface
# ============================================================================

def create_interface() -> gr.Blocks:
    """
    Create the Gradio web interface.
    """
    with gr.Blocks(
        title="PDF to Audiobook Converter",
        theme=gr.themes.Soft(),
        css="""
            .main-title {
                text-align: center;
                margin-bottom: 1rem;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 2rem;
            }
        """
    ) as app:
        gr.Markdown(
            """
            # 📚 PDF to Audiobook Converter
            
            Convert your PDF documents into high-quality audiobooks with natural-sounding voices.
            """,
            elem_classes="main-title"
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Upload & Settings")
                
                pdf_input = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                    type="filepath"
                )
                
                voice_dropdown = gr.Dropdown(
                    choices=list(POPULAR_VOICES.keys()),
                    value="en-US-AriaNeural (Female, US)",
                    label="🎙️ Voice",
                    info="Select the narrator voice"
                )
                
                speed_slider = gr.Slider(
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    label="⚡ Speed",
                    info="Adjust playback speed (1.0 = normal)"
                )
                
                convert_btn = gr.Button(
                    "🎧 Generate Audiobook",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Output")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=10,
                    interactive=False,
                    placeholder="Conversion status will appear here..."
                )
                
                zip_output = gr.File(
                    label="📥 Download All Chapters (ZIP)",
                    interactive=False
                )
        
        gr.Markdown("### 🎵 Preview Chapters")
        audio_gallery = gr.File(
            label="Generated Audio Files",
            file_count="multiple",
            interactive=False
        )
        
        # Connect the conversion function
        convert_btn.click(
            fn=convert_pdf_to_audiobook,
            inputs=[pdf_input, voice_dropdown, speed_slider],
            outputs=[status_output, zip_output, audio_gallery],
            show_progress=True
        )
        
        gr.Markdown(
            """
            ---
            ### 💡 Tips
            - **Chapter Detection**: The app automatically detects chapters based on common patterns (Chapter 1, Part I, etc.)
            - **Large PDFs**: Documents without clear chapter markers are split into ~10-page segments
            - **Voice Selection**: Try different voices to find one that suits your content
            - **Speed**: Increase speed for faster listening, decrease for complex content
            
            ---
            *Powered by [edge-tts](https://github.com/rany2/edge-tts) and [pdfplumber](https://github.com/jsvine/pdfplumber)*
            """
        )
    
    return app


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
