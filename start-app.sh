#!/bin/bash
# Make script executable with: chmod +x start-app.sh
# start-app.sh - Script to build and start the SMC Documentation Q&A System

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SMC Documentation Q&A System Launcher ===${NC}"
echo -e "${BLUE}==========================================${NC}"

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Build frontend
echo -e "${YELLOW}Building React frontend...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}Frontend build failed!${NC}"
    exit 1
fi
cd ..

echo -e "${GREEN}Frontend built successfully!${NC}"

# Start backend (Flask app)
echo -e "${YELLOW}Starting Flask backend...${NC}"
cd backend

# Try to determine the correct Python command
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo -e "${YELLOW}Using python3 command instead of python${NC}"
    else
        echo -e "${RED}Error: Neither 'python' nor 'python3' commands were found${NC}"
        echo -e "${YELLOW}Please make sure Python is installed and in your PATH${NC}"
        exit 1
    fi
fi

# Check if requirements are installed
echo -e "${YELLOW}Checking Python dependencies...${NC}"
if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
    echo -e "${YELLOW}Flask not found. Installing required dependencies...${NC}"
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install dependencies. Please install them manually:${NC}"
            echo -e "  $PYTHON_CMD -m pip install -r requirements.txt"
            exit 1
        fi
    else
        echo -e "${RED}requirements.txt not found. Installing Flask directly...${NC}"
        $PYTHON_CMD -m pip install flask python-dotenv chromadb sentence-transformers
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install dependencies. Please install them manually:${NC}"
            echo -e "  $PYTHON_CMD -m pip install flask python-dotenv chromadb sentence-transformers"
            exit 1
        fi
    fi
fi

# Execute the Python application
echo -e "${GREEN}Dependencies installed. Starting Flask app...${NC}"
$PYTHON_CMD app.py

# This part below will only run if the Flask app stops
echo -e "${YELLOW}Flask app has stopped.${NC}"
exit 0