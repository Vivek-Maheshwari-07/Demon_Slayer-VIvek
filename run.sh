#!/bin/bash

# EPISTEME One-Click Boot Script
# Spins up both FastAPI (port 8000) and Vite React (port 5173) concurrently.

# 1. Environment validation
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found in the root directory!"
    echo "Creating a dummy .env template. Please populate GEMINI_API_KEY inside it."
    echo "GEMINI_API_KEY=your_key_here" > .env
else
    # Check if GEMINI_API_KEY is defined and not placeholder
    if grep -q "GEMINI_API_KEY=your_key_here" .env || ! grep -q "GEMINI_API_KEY=" .env; then
        echo "⚠️  Warning: GEMINI_API_KEY is not configured in .env!"
        echo "Backend will operate using high-fidelity mock data responses for tests."
    fi
fi

# 2. Shutdown cleaner
cleanup() {
    echo -e "\n🛑  Shutting down EPISTEME servers..."
    # Terminate all processes in the child process group
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Trap CTRL+C, SIGINT, SIGTERM to run cleanup
trap cleanup INT TERM EXIT

echo "🚀  Booting EPISTEME Backend (Uvicorn)..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "🚀  Booting EPISTEME Frontend (Vite)..."
npm run dev --prefix frontend &
FRONTEND_PID=$!

echo "=========================================================="
echo "EPISTEME companion is launching!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "=========================================================="
echo "Press CTRL+C to cleanly terminate both servers."

# Keep parent script alive to wait for background jobs
wait
