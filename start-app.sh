#!/bin/bash

# Define color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting SMC Documentation Assistant...${NC}"

# Set directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

# Check if we're in a virtual environment already
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Not currently in a virtual environment.${NC}"
    
    # Check if venv exists
    if [[ ! -d "$VENV_DIR" ]]; then
        echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
        cd "$BACKEND_DIR" || exit 1
        python3 -m venv venv
        if [[ $? -ne 0 ]]; then
            echo -e "${RED}Failed to create virtual environment. Make sure python3-venv is installed.${NC}"
            echo -e "${YELLOW}On Ubuntu/Debian, you can install it with: sudo apt-get install python3-venv${NC}"
            exit 1
        fi
    fi
    
    # Activate the virtual environment
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    
    # Check if activation was successful
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        exit 1
    fi
    
    # Install requirements if needed
    if [[ ! -f "$VENV_DIR/requirements_installed" ]]; then
        echo -e "${YELLOW}Installing Python requirements...${NC}"
        cd "$BACKEND_DIR" || exit 1
        pip install -r requirements.txt
        if [[ $? -eq 0 ]]; then
            touch "$VENV_DIR/requirements_installed"
        else
            echo -e "${RED}Failed to install requirements.${NC}"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}Already in virtual environment: $VIRTUAL_ENV${NC}"
fi

# Build frontend if needed
if [[ ! -d "$BACKEND_DIR/static/react" || "$1" == "--rebuild" ]]; then
    echo -e "${GREEN}Building frontend...${NC}"
    cd "$FRONTEND_DIR" || exit 1
    npm install
    npm run build
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Failed to build frontend.${NC}"
        exit 1
    fi
fi

# Start backend application
echo -e "${GREEN}Starting backend server...${NC}"
cd "$BACKEND_DIR" || exit 1
python app.py

# If the backend server stops, deactivate the virtual environment
deactivate
echo -e "${YELLOW}Application stopped. Virtual environment deactivated.${NC}"