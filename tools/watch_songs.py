import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watcher.log'),
        logging.StreamHandler()
    ]
)

class SongFolderHandler(FileSystemEventHandler):
    def __init__(self, base_dir):
        self.base_dir = os.path.abspath('.')  # Use current directory as base
        self.last_update = time.time()
        
    def process_folder(self, folder_name):
        try:
            print(f"Processing folder: {folder_name}")
            subprocess.run(['python', os.path.join('tools', 'consolidate_songs.py'), '--base-dir', '.', '--output', 'consolidated_songs.yml'], check=True)
            subprocess.run(['python', os.path.join('tools', 'generate_song_metadata.py'), '--base-dir', '.', '--output', 'song_metadata.yml'], check=True)
            print("Both files updated successfully!")
        except Exception as e:
            print(f"Error processing folder: {e}")

    def on_created(self, event):
        print(f"\nEvent: {event.event_type}")
        print(f"Path: {event.src_path}")
        print(f"Is directory: {event.is_directory}")
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
        else:
            folder_name = '.'  # Root directory
        print(f"Folder: {folder_name}")
        print("Processing...")
        self.process_folder(folder_name)

    def on_deleted(self, event):
        print(f"\nEvent: {event.event_type}")
        print(f"Path: {event.src_path}")
        print(f"Is directory: {event.is_directory}")
        if event.is_directory:
            folder_name = os.path.basename(event.src_path)
        else:
            folder_name = '.'  # Root directory
        print(f"Folder: {folder_name}")
        print("Processing...")
        self.process_folder(folder_name)

    def on_moved(self, event):
        print(f"\nEvent: {event.event_type}")
        print(f"From: {event.src_path}")
        print(f"To: {event.dest_path}")
        print(f"Is directory: {event.is_directory}")
        if event.is_directory:
            old_folder = os.path.basename(event.src_path)
            new_folder = os.path.basename(event.dest_path)
        else:
            old_folder = '.'  # Root directory
            new_folder = '.'  # Root directory
        print(f"Old Folder: {old_folder}")
        print(f"New Folder: {new_folder}")
        print("Processing...")
        
        # Update metadata if this is a folder rename
        metadata_file = "song_metadata.yml"
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                
                # Update folder name in metadata
                if old_folder in metadata.get("songs", {}):
                    song_data = metadata["songs"][old_folder]
                    del metadata["songs"][old_folder]
                    metadata["songs"][new_folder] = song_data
                    
                    # Update the lyrics file name in metadata
                    if "original_lyrics_name" in song_data:
                        old_lyrics_name = song_data["original_lyrics_name"]
                        # Replace old folder name with new folder name in lyrics file name
                        new_lyrics_name = old_lyrics_name.replace(f"{old_folder}_", f"{new_folder}_")
                        song_data["original_lyrics_name"] = new_lyrics_name
                    
                    # Save updated metadata
                    with open(metadata_file, "w", encoding='utf-8') as f:
                        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            except Exception as e:
                print(f"Error updating metadata for folder rename: {str(e)}")
        
        # Process the new folder
        self.process_folder(new_folder)

    def on_modified(self, event):
        print(f"\nEvent: {event.event_type}")
        print(f"Path: {event.src_path}")
        print(f"Is directory: {event.is_directory}")
        
        # Only process if enough time has passed since last update
        current_time = time.time()
        if current_time - self.last_update > 2:  # 2 seconds delay
            folder_name = '.'  # Root directory
            print(f"Folder: {folder_name}")
            print("Processing...")
            self.process_folder(folder_name)
            self.last_update = current_time
            return  # Add return to prevent further processing

def start_watcher():
    print("Starting song folder watcher in foreground...")
    print("Use Ctrl+C to stop")
    
    event_handler = SongFolderHandler('.')
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            # Print a heartbeat message every 30 seconds to show it's running
            if time.time() - event_handler.last_update > 30:
                print("Watcher is running...")
                event_handler.last_update = time.time()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def stop_watcher():
    import psutil
    import signal
    
    print("Stopping song folder watcher...")
    
    # Find and terminate the watcher process
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'python' and any('watch_songs.py' in arg for arg in proc.cmdline()):
            try:
                proc.send_signal(signal.SIGINT)
                print(f"Stopped process: {proc.pid}")
            except psutil.NoSuchProcess:
                pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python watch_songs.py start|stop")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "start":
        start_watcher()
    elif command == "stop":
        stop_watcher()
    else:
        print("Invalid command. Use start or stop.")

if __name__ == "__main__":
    main()
