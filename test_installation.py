#!/usr/bin/env python
"""
Quick test script to verify the installation works correctly.
Run this after installing dependencies to ensure everything is set up.
"""

import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import pdfplumber
        print("  ✅ pdfplumber")
    except ImportError as e:
        print(f"  ❌ pdfplumber: {e}")
        return False
    
    try:
        import edge_tts
        print("  ✅ edge_tts")
    except ImportError as e:
        print(f"  ❌ edge_tts: {e}")
        return False
    
    try:
        import gradio
        print(f"  ✅ gradio (version {gradio.__version__})")
    except ImportError as e:
        print(f"  ❌ gradio: {e}")
        return False
    
    return True


async def test_edge_tts():
    """Test that edge-tts can connect to Microsoft's service."""
    import edge_tts
    
    print("\nTesting edge-tts connection...")
    
    try:
        voices = await edge_tts.list_voices()
        en_voices = [v for v in voices if v['Locale'].startswith('en-')]
        print(f"  ✅ Connected! Found {len(en_voices)} English voices")
        print(f"  Sample voices:")
        for v in en_voices[:3]:
            print(f"    - {v['ShortName']} ({v['Gender']})")
        return True
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print("  Make sure you have an internet connection.")
        return False


def test_pdf_extraction():
    """Test PDF extraction with a simple example."""
    import pdfplumber
    from io import BytesIO
    
    print("\nTesting PDF extraction...")
    
    # We can't create a real PDF here, but we can verify pdfplumber works
    try:
        # This will fail but verifies the module is working
        with pdfplumber.open(BytesIO(b"not a pdf")) as pdf:
            pass
    except Exception as e:
        if "PDF" in str(e) or "file" in str(e).lower():
            print("  ✅ pdfplumber is working (correctly rejected invalid PDF)")
            return True
        else:
            print(f"  ⚠️ Unexpected error: {e}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("PDF to Audiobook - Installation Test")
    print("=" * 50 + "\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n❌ Import test failed. Run: pip install -r requirements.txt")
        return 1
    
    # Test PDF extraction
    if not test_pdf_extraction():
        all_passed = False
    
    # Test edge-tts connection
    import asyncio
    try:
        if not asyncio.run(test_edge_tts()):
            all_passed = False
    except Exception as e:
        print(f"\n⚠️ Could not test edge-tts: {e}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! You can now run: python app.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
