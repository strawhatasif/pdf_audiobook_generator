#!/usr/bin/env bash
#
# PDF to Audiobook Generator - Run Script
# Compatible with: GitBash (Windows), macOS, Linux
#

set -e

# Colors for output (works in most terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📚 PDF to Audiobook Generator            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS="Linux";;
        Darwin*)    OS="Mac";;
        CYGWIN*)    OS="Windows";;
        MINGW*)     OS="Windows";;  # GitBash
        MSYS*)      OS="Windows";;  # GitBash
        *)          OS="Unknown";;
    esac
    echo -e "${YELLOW}Detected OS:${NC} $OS"
}

# Find Python command
find_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found! Please install Python 3.9 or higher.${NC}"
        exit 1
    fi
    
    # Verify Python version
    PY_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${YELLOW}Python version:${NC} $PY_VERSION"
}

# Create virtual environment if it doesn't exist
setup_venv() {
    if [ ! -d "venv" ]; then
        echo -e "\n${YELLOW}Creating virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
}

# Activate virtual environment
activate_venv() {
    echo -e "\n${YELLOW}Activating virtual environment...${NC}"
    
    if [ "$OS" = "Windows" ]; then
        # GitBash on Windows
        source venv/Scripts/activate
    else
        # Mac/Linux
        source venv/bin/activate
    fi
    
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
}

# Install dependencies
install_deps() {
    echo -e "\n${YELLOW}Checking dependencies...${NC}"
    
    # Check if packages are installed
    if ! $PYTHON_CMD -c "import gradio, pdfplumber, edge_tts" 2>/dev/null; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements.txt --quiet
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ Dependencies already installed${NC}"
    fi
}

# Run the application
run_app() {
    echo -e "\n${GREEN}🚀 Starting PDF to Audiobook Generator...${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "The app will open in your browser at:"
    echo -e "${GREEN}   http://127.0.0.1:7860${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"
    
    $PYTHON_CMD app.py
}

# Main execution
main() {
    detect_os
    find_python
    setup_venv
    activate_venv
    install_deps
    run_app
}

main
