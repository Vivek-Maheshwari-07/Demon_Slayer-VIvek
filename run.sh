#!/usr/bin/env bash

# EPISTEME One-Click Application Launcher
# Boots FastAPI backend and Vite React frontend concurrently.

echo "============================================================"
echo "🚀 Starting EPISTEME Research Engine..."
echo "============================================================"

# 1. Environment File Check
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found in root directory."
    echo "GEMINI_API_KEY=" > .env
    echo "Created a template .env file. Add your GEMINI_API_KEY for live LLM features."
fi

# 2. Cleanup Handler for Graceful Exit (CTRL+C)
cleanup() {
    echo ""
    echo "============================================================"
    echo "🛑 Shutting down EPISTEME servers..."
    echo "============================================================"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup INT TERM EXIT

# 3. Boot Backend Server (FastAPI on Port 8000)
echo "📦 Booting FastAPI Backend Server (http://localhost:8000)..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait briefly for backend startup
sleep 2

# 4. Boot Frontend Server (Vite React on Port 5173)
echo "💻 Booting React Vite Frontend Server (http://localhost:5173)..."
if [ -d "frontend" ]; then
    cd frontend && npm run dev &
    FRONTEND_PID=$!
    cd ..
else
    echo "❌ Error: 'frontend' directory not found!"
    exit 1
fi

echo "============================================================"
echo "✨ EPISTEME is live! Press CTRL+C to terminate all services."
echo "============================================================"

# Wait for background jobs
wait
