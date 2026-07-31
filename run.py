import subprocess
import sys
import time
import os

print("=" * 60)
print("🚀 Launching EPISTEME Backend & Frontend...")
print("=" * 60)

# Ensure .env file exists
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("OPENROUTER_API_KEY=\n")
    print("⚠️  Created template .env file. Add your OPENROUTER_API_KEY if needed.")

# Start FastAPI backend
print("📦 Starting FastAPI Backend (http://localhost:8000)...")
backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]
backend_proc = subprocess.Popen(backend_cmd)

# Wait briefly for backend startup
time.sleep(2)

# Start Vite React frontend
print("💻 Starting Vite React Frontend (http://localhost:5173)...")
frontend_dir = os.path.join(os.getcwd(), "frontend")

if sys.platform == "win32":
    frontend_proc = subprocess.Popen("npm run dev", cwd=frontend_dir, shell=True)
else:
    frontend_proc = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)

print("\n" + "=" * 60)
print("✨ EPISTEME is live! Open http://localhost:5173 in your browser.")
print("Press CTRL+C in this terminal to stop both servers cleanly.")
print("=" * 60 + "\n")

try:
    # Wait for execution or CTRL+C
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down EPISTEME background servers...")
    backend_proc.terminate()
    frontend_proc.terminate()
    sys.exit(0)
