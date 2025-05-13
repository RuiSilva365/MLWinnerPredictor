#!/bin/bash
# start_servers.sh

# File paths
GO_API_PATH="/Users/enlt-rsilva/ExampleApi"
ML_PREDICTOR_PATH="/Users/enlt-rsilva/FootPred/MLWinnerPredictor"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists go; then
    echo "Error: Go is not installed. Please install Go before running this script."
    exit 1
fi

if ! command_exists python3; then
    echo "Error: Python 3 is not installed. Please install Python 3 before running this script."
    exit 1
fi

# Create log directory if it doesn't exist
mkdir -p $ML_PREDICTOR_PATH/logs

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Football Predictor API Startup ===${NC}"

# First navigate to the ML predictor directory
cd $ML_PREDICTOR_PATH

# Start Python API server
echo -e "${YELLOW}Starting Python API server...${NC}"
python3 api_handler.py > logs/python_api.log 2>&1 &
PYTHON_PID=$!
echo -e "${GREEN}Python API server started with PID ${PYTHON_PID}${NC}"

# Wait for Python server to initialize
echo "Waiting for Python API to initialize (5 seconds)..."
sleep 5

# Navigate to the Go API directory
cd $GO_API_PATH

# Build and run Go API server
echo -e "${YELLOW}Building and starting Go API server...${NC}"
go run main.go > $ML_PREDICTOR_PATH/logs/go_api.log 2>&1 &
GO_PID=$!
echo -e "${GREEN}Go API server started with PID ${GO_PID}${NC}"

# Wait for Go server to initialize
echo "Waiting for Go API to initialize (3 seconds)..."
sleep 3

# Save PIDs to file for easy shutdown
echo "$PYTHON_PID $GO_PID" > $ML_PREDICTOR_PATH/.server_pids

# Go back to the ML predictor directory
cd $ML_PREDICTOR_PATH

echo -e "${GREEN}Both servers are now running:${NC}"
echo -e "  Python API: ${BLUE}http://localhost:5000${NC}"
echo -e "  Go API: ${BLUE}http://localhost:8080${NC}"
echo
echo -e "Use ${YELLOW}./stop_servers.sh${NC} to stop the servers"
echo -e "Use ${YELLOW}./test_api.py${NC} to test the API"
echo
echo -e "Server logs are available in the ${BLUE}logs/${NC} directory"