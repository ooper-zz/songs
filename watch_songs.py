import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess

class SongFolderHandler(FileSystemEventHandler):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.last_update = time.time()
        
    def process_folder(self, folder_name):
        try:
            # Run both consolidation scripts
            print(f"Processing folder: {folder_name}")
            
            # Run consolidate_songs.py
            print("Updating consolidated_songs.yml...")
            subprocess.run(['python', 'consolidate_songs.py', '--base-dir', self.base_dir, '--output', os.path.join(self.base_dir, 'consolidated_songs.yml')], check=True)
            
            # Run generate_song_tags.py
            print("Updating song_tags.yml...")
            subprocess.run(['python', 'generate_song_tags.py', '--base-dir', self.base_dir, '--output', os.path.join(self.base_dir, 'song_tags.yml')], check=True)
            
            print("Both files updated successfully!")
        except Exception as e:
            print(f"Error processing folder: {e}")

    def on_created(self, event):
        if not event.is_directory:
            return
        folder_name = os.path.basename(event.src_path)
        self.process_folder(folder_name)

    def on_deleted(self, event):
        if not event.is_directory:
            return
        folder_name = os.path.basename(event.src_path)
        self.process_folder(folder_name)

    def on_moved(self, event):
        if not event.is_directory:
            return
        folder_name = os.path.basename(event.dest_path)
        self.process_folder(folder_name)

    def on_modified(self, event):
        if not event.is_directory:
            return
        # Only process if enough time has passed since last update
        current_time = time.time()
        if current_time - self.last_update > 2:  # 2 seconds delay
            folder_name = os.path.basename(event.src_path)
            self.process_folder(folder_name)
            self.last_update = current_time

def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Starting song folder watcher...")
    print("Press Ctrl+C to stop")
    
    event_handler = SongFolderHandler(base_dir)
    observer = Observer()
    observer.schedule(event_handler, base_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
