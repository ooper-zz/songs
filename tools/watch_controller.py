import subprocess
import os
import signal
import sys
import time

class WatchService:
    def __init__(self):
        self.process = None
        self.pid_file = os.path.expanduser("~/Library/Application Support/Songs/watch.pid")

    def start(self):
        """Start the watch service"""
        if self.is_running():
            print("Watch service is already running")
            return

        try:
            # Start the watch script in a new process
            self.process = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "watch_songs.py")])
            
            # Save the PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.process.pid))
            
            print("Watch service started successfully")
        except Exception as e:
            print(f"Error starting watch service: {str(e)}")

    def stop(self):
        """Stop the watch service"""
        if not self.is_running():
            print("Watch service is not running")
            return

        try:
            # Read the PID from file
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Send SIGTERM to the process
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            time.sleep(1)
            
            # Remove PID file
            os.remove(self.pid_file)
            
            print("Watch service stopped successfully")
        except Exception as e:
            print(f"Error stopping watch service: {str(e)}")

    def is_running(self):
        """Check if the service is running"""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # This will raise OSError if process doesn't exist
                return True
            except OSError:
                return False
        except:
            return False

    def status(self):
        """Get the status of the service"""
        if self.is_running():
            print("Watch service is running")
        else:
            print("Watch service is not running")

def main():
    service = WatchService()
    
    if len(sys.argv) < 2:
        print("Usage: python watch_controller.py [start|stop|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        service.start()
    elif command == 'stop':
        service.stop()
    elif command == 'status':
        service.status()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python watch_controller.py [start|stop|status]")
        sys.exit(1)

if __name__ == "__main__":
    main()
