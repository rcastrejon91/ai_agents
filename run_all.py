#!/usr/bin/env python3
# run_all.py

"""
Lyra AI Platform - Complete System Launcher
Starts all components: Web, API, Agents, Gateway, and Lyra Core
"""

import os
import sys
import time
import signal
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional
import threading
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class Color:
    """Terminal colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ProcessManager:
    """Manages multiple processes"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.threads: List[threading.Thread] = []
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n\n{Color.WARNING}🛑 Shutdown signal received...{Color.ENDC}")
        self.shutdown()
        sys.exit(0)
    
    def start_process(
        self, 
        name: str, 
        command: List[str], 
        cwd: Optional[Path] = None,
        env: Optional[Dict] = None,
        color: str = Color.OKBLUE
    ):
        """Start a process and monitor it"""
        print(f"{color}🚀 Starting {name}...{Color.ENDC}")
        
        try:
            # Merge environment variables
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Start process
            process = subprocess.Popen(
                command,
                cwd=cwd or project_root,
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes[name] = process
            
            # Start output monitoring threads
            stdout_thread = threading.Thread(
                target=self._monitor_output,
                args=(name, process.stdout, color),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._monitor_output,
                args=(name, process.stderr, Color.FAIL),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            self.threads.extend([stdout_thread, stderr_thread])
            
            # Give process time to start
            time.sleep(1)
            
            # Check if process started successfully
            if process.poll() is None:
                print(f"{Color.OKGREEN}✅ {name} started successfully{Color.ENDC}")
                return True
            else:
                print(f"{Color.FAIL}❌ {name} failed to start{Color.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Color.FAIL}❌ Error starting {name}: {e}{Color.ENDC}")
            return False
    
    def _monitor_output(self, name: str, stream, color: str):
        """Monitor process output"""
        try:
            for line in stream:
                if self.running and line.strip():
                    print(f"{color}[{name}]{Color.ENDC} {line.strip()}")
        except Exception:
            pass
    
    def check_processes(self):
        """Check status of all processes"""
        print(f"\n{Color.HEADER}📊 Process Status:{Color.ENDC}")
        all_running = True
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"  {Color.OKGREEN}✅ {name}: Running (PID: {process.pid}){Color.ENDC}")
            else:
                print(f"  {Color.FAIL}❌ {name}: Stopped{Color.ENDC}")
                all_running = False
        
        return all_running
    
    def shutdown(self):
        """Shutdown all processes gracefully"""
        print(f"\n{Color.WARNING}🛑 Shutting down all processes...{Color.ENDC}")
        self.running = False
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"  Stopping {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"  Force killing {name}...")
                    process.kill()
                except Exception as e:
                    print(f"  Error stopping {name}: {e}")
        
        print(f"{Color.OKGREEN}✅ All processes stopped{Color.ENDC}")


def print_banner():
    """Print startup banner"""
    banner = f"""
{Color.HEADER}{Color.BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                  🧠 LYRA AI PLATFORM LAUNCHER                    ║
║                                                                   ║
║              Multi-Perspective Orchestrator System                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Color.ENDC}
"""
    print(banner)


def check_dependencies():
    """Check if required dependencies are installed"""
    print(f"{Color.HEADER}🔍 Checking dependencies...{Color.ENDC}")
    
    issues = []
    
    # Check Python packages
    required_packages = [
        "flask",
        "openai",
        "anthropic",
        "numpy",
        "pandas",
        "nltk"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {Color.OKGREEN}✅ {package}{Color.ENDC}")
        except ImportError:
            print(f"  {Color.FAIL}❌ {package} - Not installed{Color.ENDC}")
            issues.append(f"Python package: {package}")
    
    # Check Node.js
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  {Color.OKGREEN}✅ Node.js {result.stdout.strip()}{Color.ENDC}")
        else:
            print(f"  {Color.FAIL}❌ Node.js - Not found{Color.ENDC}")
            issues.append("Node.js")
    except FileNotFoundError:
        print(f"  {Color.FAIL}❌ Node.js - Not found{Color.ENDC}")
        issues.append("Node.js")
    
    # Check npm
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  {Color.OKGREEN}✅ npm {result.stdout.strip()}{Color.ENDC}")
        else:
            print(f"  {Color.FAIL}❌ npm - Not found{Color.ENDC}")
            issues.append("npm")
    except FileNotFoundError:
        print(f"  {Color.FAIL}❌ npm - Not found{Color.ENDC}")
        issues.append("npm")
    
    # Check .env file
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"  {Color.OKGREEN}✅ .env configuration file{Color.ENDC}")
    else:
        print(f"  {Color.WARNING}⚠️  .env file not found (will use defaults){Color.ENDC}")
    
    if issues:
        print(f"\n{Color.WARNING}⚠️  Missing dependencies:{Color.ENDC}")
        for issue in issues:
            print(f"  • {issue}")
        print(f"\n{Color.WARNING}Run 'npm run setup' to install dependencies{Color.ENDC}")
        return False
    
    print(f"\n{Color.OKGREEN}✅ All dependencies satisfied{Color.ENDC}")
    return True


def start_companion_api(pm: ProcessManager):
    """Start Companion API"""
    api_path = project_root / "apps" / "companion_api"
    
    if not api_path.exists():
        print(f"{Color.WARNING}⚠️  Companion API not found, skipping...{Color.ENDC}")
        return False
    
    return pm.start_process(
        "API",
        ["npm", "run", "dev"],
        cwd=api_path,
        color=Color.OKCYAN
    )


def start_companion_web(pm: ProcessManager):
    """Start Companion Web"""
    web_path = project_root / "apps" / "companion_web"
    
    if not web_path.exists():
        print(f"{Color.WARNING}⚠️  Companion Web not found, skipping...{Color.ENDC}")
        return False
    
    return pm.start_process(
        "WEB",
        ["npm", "run", "dev"],
        cwd=web_path,
        color=Color.HEADER
    )


def start_agent_gateway(pm: ProcessManager):
    """Start Agent Gateway"""
    gateway_file = project_root / "api_gateway.py"
    
    if not gateway_file.exists():
        print(f"{Color.WARNING}⚠️  Agent Gateway not found, skipping...{Color.ENDC}")
        return False
    
    return pm.start_process(
        "GATEWAY",
        [sys.executable, "api_gateway.py"],
        color=Color.OKGREEN
    )


def start_lyra_core(pm: ProcessManager):
    """Start Lyra Core"""
    lyra_file = project_root / "lyra_core" / "lyra_ai.py"
    
    if not lyra_file.exists():
        # Try alternative location
        lyra_file = project_root / "main.py"
        if not lyra_file.exists():
            print(f"{Color.WARNING}⚠️  Lyra Core not found, skipping...{Color.ENDC}")
            return False
    
    return pm.start_process(
        "LYRA",
        [sys.executable, str(lyra_file)],
        color=Color.WARNING
    )


def start_all_services(pm: ProcessManager, components: List[str]):
    """Start all selected services"""
    print(f"\n{Color.HEADER}🚀 Starting services...{Color.ENDC}\n")
    
    started = []
    failed = []
    
    if "api" in components:
        if start_companion_api(pm):
            started.append("Companion API")
        else:
            failed.append("Companion API")
        time.sleep(2)
    
    if "web" in components:
        if start_companion_web(pm):
            started.append("Companion Web")
        else:
            failed.append("Companion Web")
        time.sleep(2)
    
    if "gateway" in components:
        if start_agent_gateway(pm):
            started.append("Agent Gateway")
        else:
            failed.append("Agent Gateway")
        time.sleep(2)
    
    if "lyra" in components:
        if start_lyra_core(pm):
            started.append("Lyra Core")
        else:
            failed.append("Lyra Core")
    
    # Print summary
    print(f"\n{Color.HEADER}{'='*70}{Color.ENDC}")
    print(f"{Color.BOLD}Startup Summary:{Color.ENDC}")
    
    if started:
        print(f"\n{Color.OKGREEN}✅ Started ({len(started)}):{Color.ENDC}")
        for service in started:
            print(f"  • {service}")
    
    if failed:
        print(f"\n{Color.FAIL}❌ Failed ({len(failed)}):{Color.ENDC}")
        for service in failed:
            print(f"  • {service}")
    
    print(f"\n{Color.HEADER}{'='*70}{Color.ENDC}")


def print_access_info():
    """Print access information"""
    info = f"""
{Color.OKGREEN}{Color.BOLD}🌐 Access Information:{Color.ENDC}

  {Color.OKCYAN}Companion Web:{Color.ENDC}    http://localhost:3000
  {Color.OKCYAN}Companion API:{Color.ENDC}    http://localhost:3001
  {Color.OKCYAN}Agent Gateway:{Color.ENDC}    http://localhost:8000
  {Color.OKCYAN}Lyra Core:{Color.ENDC}        http://localhost:5000

{Color.WARNING}📝 Commands:{Color.ENDC}
  • Press {Color.BOLD}Ctrl+C{Color.ENDC} to stop all services
  • Check logs in the terminal output above
  • View individual service status in their respective windows

{Color.HEADER}{'='*70}{Color.ENDC}
"""
    print(info)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Lyra AI Platform Launcher"
    )
    parser.add_argument(
        "--components",
        nargs="+",
        choices=["api", "web", "gateway", "lyra", "all"],
        default=["all"],
        help="Components to start (default: all)"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip dependency check"
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip startup banner"
    )
    
    args = parser.parse_args()
    
    # Print banner
    if not args.no_banner:
        print_banner()
    
    # Check dependencies
    if not args.skip_check:
        if not check_dependencies():
            response = input(f"\n{Color.WARNING}Continue anyway? (y/N): {Color.ENDC}")
            if response.lower() != 'y':
                print(f"\n{Color.FAIL}Aborted.{Color.ENDC}")
                sys.exit(1)
    
    # Determine components to start
    components = args.components
    if "all" in components:
        components = ["api", "web", "gateway", "lyra"]
    
    print(f"\n{Color.HEADER}Components to start:{Color.ENDC} {', '.join(components)}")
    
    # Create process manager
    pm = ProcessManager()
    
    try:
        # Start services
        start_all_services(pm, components)
        
        # Print access info
        print_access_info()
        
        # Check initial status
        time.sleep(2)
        pm.check_processes()
        
        # Keep running
        print(f"\n{Color.OKGREEN}✨ Lyra AI Platform is running!{Color.ENDC}")
        print(f"{Color.WARNING}Press Ctrl+C to stop all services{Color.ENDC}\n")
        
        # Monitor processes
        while pm.running:
            time.sleep(5)
            
            # Check if any process died
            for name, process in pm.processes.items():
                if process.poll() is not None:
                    print(f"\n{Color.FAIL}❌ {name} stopped unexpectedly{Color.ENDC}")
                    pm.shutdown()
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Color.WARNING}Keyboard interrupt received{Color.ENDC}")
    except Exception as e:
        print(f"\n{Color.FAIL}❌ Error: {e}{Color.ENDC}")
    finally:
        pm.shutdown()
        print(f"\n{Color.OKGREEN}👋 Lyra AI Platform stopped{Color.ENDC}\n")


if __name__ == "__main__":
    main()
