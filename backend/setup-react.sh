#!/bin/bash
# This script sets up the React frontend for the SMC Documentation Q&A System

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SMC Documentation Q&A System - React Setup ===${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check if node and npm are installed
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: Node.js and npm are required but not installed.${NC}"
    echo -e "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v)
echo -e "${GREEN}Node.js version:${NC} $NODE_VERSION"

# Create the frontend directory if it doesn't exist
if [ ! -d "frontend" ]; then
    echo -e "${YELLOW}Creating frontend directory...${NC}"
    mkdir -p frontend
fi

# Navigate to frontend directory
cd frontend

# Initialize a new Vite React project
echo -e "${YELLOW}Initializing new Vite React project...${NC}"
npm create vite@latest . -- --template react

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install
npm install axios tailwindcss postcss autoprefixer lucide-react clsx react-markdown

# Setup Tailwind CSS
echo -e "${YELLOW}Setting up Tailwind CSS...${NC}"
npx tailwindcss init -p

# Create project structure
echo -e "${YELLOW}Creating project structure...${NC}"
mkdir -p src/components src/hooks

# Add Flask route to serve React build
echo -e "${YELLOW}Adding Flask route to serve React build...${NC}"
cd ..
if [ -f "app.py" ]; then
    # Check if the route already exists
    if ! grep -q "def serve_react" app.py; then
        echo '
# Serve React frontend
from flask import send_from_directory

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Serve React frontend."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, "react", path)):
        return send_from_directory(os.path.join(app.static_folder, "react"), path)
    return send_from_directory(os.path.join(app.static_folder, "react"), "index.html")' >> app.py
        
        echo -e "${GREEN}Added React serving route to app.py${NC}"
    else
        echo -e "${YELLOW}Flask route for React already exists in app.py${NC}"
    fi
else
    echo -e "${RED}Warning: app.py not found. You'll need to manually add the React serving route.${NC}"
fi

# Create directory for React build
mkdir -p static/react

echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Navigate to the frontend directory: cd frontend"
echo "2. Add all the component files shown in the React Implementation documentation"
echo "3. For development, run: npm run dev"
echo "4. To build for production: npm run build"
echo "5. Run the Flask app to serve both backend and frontend: python app.py"
echo -e "${BLUE}=================================================${NC}"