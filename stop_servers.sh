#!/bin/bash
# stop_servers.sh

# File path
ML_PREDICTOR_PATH="C:/Users/smash/MLWinnerPredictor"

# Change to the ML predictor directory
cd $ML_PREDICTOR_PATH

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Stopping Football Predictor API Servers ===${NC}"

# Check if PIDs file exists
if [ ! -f .server_pids ]; then
    echo -e "${RED}No server PIDs file found. Servers might not be running.${NC}"
    
    # Try to find and kill the processes anyway
    echo -e "${YELLOW}Attempting to find and kill the server processes...${NC}"
    
    # Find Python API process
    PYTHON_PID=$(pgrep -f "python3 api_handler.py")
    if [ -n "$PYTHON_PID" ]; then
        echo -e "Stopping Python API server (PID: ${PYTHON_PID})..."
        kill $PYTHON_PID
        echo -e "${GREEN}Python API server stopped${NC}"
    else
        echo -e "${YELLOW}No Python API server process found${NC}"
    fi
    
    # Find Go API process
    GO_PID=$(pgrep -f "go run.*main.go")
    if [ -n "$GO_PID" ]; then
        echo -e "Stopping Go API server (PID: ${GO_PID})..."
        kill $GO_PID
        echo -e "${GREEN}Go API server stopped${NC}"
    else
        echo -e "${YELLOW}No Go API server process found${NC}"
    fi
    
    exit 0
fi

# Read PIDs from file
read PYTHON_PID GO_PID < .server_pids

# Stop Python API server
if ps -p $PYTHON_PID > /dev/null; then
    echo -e "Stopping Python API server (PID: ${PYTHON_PID})..."
    kill $PYTHON_PID
    echo -e "${GREEN}Python API server stopped${NC}"
else
    echo -e "${YELLOW}Python API server (PID: ${PYTHON_PID}) is not running${NC}"
fi

# Stop Go API server
if ps -p $GO_PID > /dev/null; then
    echo -e "Stopping Go API server (PID: ${GO_PID})..."
    kill $GO_PID
    echo -e "${GREEN}Go API server stopped${NC}"
else
    echo -e "${YELLOW}Go API server (PID: ${GO_PID}) is not running${NC}"
fi

# Remove PIDs file
rm .server_pids

echo -e "${GREEN}All servers have been stopped${NC}"