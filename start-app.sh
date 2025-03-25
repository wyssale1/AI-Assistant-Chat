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
python app.py

# This part below will only run if the Flask app stops
echo -e "${YELLOW}Flask app has stopped.${NC}"
exit 0