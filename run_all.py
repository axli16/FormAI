"""
JointTrack - Complete Application Launcher
Starts all services with a single command:
- Flask Backend (MediaPipe + Kafka Producer)
- AI Feedback Service (Kafka Consumer + Vertex AI)
- React Frontend (UI)

Usage: python run_all.py
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_service(name, status="STARTING"):
    color = Colors.GREEN if status == "RUNNING" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.END} {Colors.BOLD}{name}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ ERROR: {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Store process handles
processes = []

def cleanup():
    """Kill all child processes on exit"""
    print_header("SHUTTING DOWN")
    for proc_name, proc in processes:
        try:
            print(f"Stopping {proc_name}...")
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    print_success("All services stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n")
    cleanup()
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required_python = [
        'flask', 'flask_cors', 'confluent_kafka', 'python-dotenv',
        'opencv-python', 'mediapipe', 'numpy'
    ]
    
    missing = []
    for package in required_python:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"Python: {package}")
        except ImportError:
            missing.append(package)
            print_error(f"Missing: {package}")
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Install with: pip install " + " ".join(missing))
        return False
    
    # Check if React dependencies are installed
    node_modules = Path("calisthenics-tracker/node_modules")
    if not node_modules.exists():
        print_error("React dependencies not installed")
        print_info("Run: cd calisthenics-tracker && npm install")
        return False
    else:
        print_success("React: node_modules found")
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("CHECKING CONFIGURATION")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env file not found")
        print_info("Copy .env.example to .env and fill in your credentials")
        return False
    
    required_vars = [
        'CONFLUENT_BOOTSTRAP_SERVERS',
        'CONFLUENT_API_KEY',
        'CONFLUENT_API_SECRET'
    ]
    
    with open(env_file) as f:
        content = f.read()
    
    missing = []
    for var in required_vars:
        if var not in content or f"{var}=your-" in content:
            missing.append(var)
            print_error(f"Missing or not configured: {var}")
        else:
            print_success(f"Configured: {var}")
    
    if missing:
        print_error("Please configure your .env file")
        return False
    
    return True

def start_flask():
    """Start Flask backend"""
    print_service("Flask Backend (Port 5000)", "STARTING")
    
    proc = subprocess.Popen(
        [sys.executable, "FlaskServer.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    processes.append(("Flask Backend", proc))
    
    # Wait for Flask to start
    print_info("Waiting for Flask to initialize...")
    time.sleep(3)
    
    if proc.poll() is None:
        print_service("Flask Backend (Port 5000)", "RUNNING")
        return True
    else:
        print_error("Flask failed to start")
        return False

def start_ai_service():
    """Start AI Feedback Service"""
    print_service("AI Feedback Service", "STARTING")
    
    proc = subprocess.Popen(
        [sys.executable, "ai_feedback_service.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    processes.append(("AI Feedback Service", proc))
    
    # Wait for AI service to start
    print_info("Waiting for AI service to initialize...")
    time.sleep(2)
    
    if proc.poll() is None:
        print_service("AI Feedback Service", "RUNNING")
        return True
    else:
        print_error("AI service failed to start")
        return False

def start_react():
    """Start React frontend"""
    print_service("React Frontend (Port 3000)", "STARTING")
    
    # Determine the correct npm command based on OS
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    proc = subprocess.Popen(
        [npm_cmd, "start"],
        cwd="calisthenics-tracker",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        shell=True if sys.platform == "win32" else False
    )
    
    processes.append(("React Frontend", proc))
    
    # Wait for React to compile
    print_info("Waiting for React to compile (this may take 10-20 seconds)...")
    time.sleep(15)
    
    if proc.poll() is None:
        print_service("React Frontend (Port 3000)", "RUNNING")
        return True
    else:
        print_error("React failed to start")
        return False

def show_status():
    """Show running services and URLs"""
    print_header("APPLICATION READY")
    
    print(f"{Colors.BOLD}Services Running:{Colors.END}")
    print(f"  {Colors.GREEN}●{Colors.END} Flask Backend:        http://localhost:5000")
    print(f"  {Colors.GREEN}●{Colors.END} AI Feedback Service:  Running in background")
    print(f"  {Colors.GREEN}●{Colors.END} React Frontend:       http://localhost:3000")
    
    print(f"\n{Colors.BOLD}Quick Start:{Colors.END}")
    print(f"  1. Open browser to: {Colors.CYAN}http://localhost:3000{Colors.END}")
    print(f"  2. Select an exercise from dropdown")
    print(f"  3. Perform the movement in front of camera")
    print(f"  4. Get real-time AI feedback!")
    
    print(f"\n{Colors.BOLD}Data Flow:{Colors.END}")
    print(f"  Camera → Flask → Kafka (pose-stream) → AI Service → Kafka (feedback-stream) → React")
    
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all services{Colors.END}\n")

def tail_logs():
    """Show live logs from all services"""
    print_header("LIVE LOGS")
    print(f"{Colors.YELLOW}Showing combined logs from all services...{Colors.END}\n")
    
    try:
        while True:
            for proc_name, proc in processes:
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line:
                        print(f"[{proc_name}] {line.rstrip()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def main():
    """Main launcher"""
    print_header("JOINTTRACK - REAL-TIME AI COACHING")
    print(f"{Colors.BOLD}Starting all services...{Colors.END}\n")
    
    # Pre-flight checks
    if not check_dependencies():
        print_error("Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    if not check_env_file():
        print_error("Configuration check failed. Please configure .env file.")
        sys.exit(1)
    
    print_success("All checks passed!\n")
    
    # Start services
    print_header("STARTING SERVICES")
    
    if not start_flask():
        cleanup()
        sys.exit(1)
    
    if not start_ai_service():
        cleanup()
        sys.exit(1)
    
    if not start_react():
        cleanup()
        sys.exit(1)
    
    # Show status
    show_status()
    
    # Keep running and show logs
    try:
        tail_logs()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        cleanup()
        sys.exit(1)
