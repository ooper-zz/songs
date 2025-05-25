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
            subprocess.run(['python', os.path.join('tools', 'consolidate_songs.py'), '--base-dir', self.base_dir, '--output', os.path.join(self.base_dir, 'consolidated_songs.yml')], check=True)
            
            # Run generate_song_tags.py
            print("Updating song_tags.yml...")
            subprocess.run(['python', os.path.join('tools', 'generate_song_tags.py'), '--base-dir', self.base_dir, '--output', os.path.join(self.base_dir, 'song_tags.yml')], check=True)
            
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
            
        # Get old and new folder names
        old_folder = os.path.basename(event.src_path)
        new_folder = os.path.basename(event.dest_path)
        
        # Update metadata if this is a folder rename
        metadata_file = os.path.join(self.base_dir, "song_tags.yml")
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
                    print(f"Updated metadata for folder rename: {old_folder} -> {new_folder}")
            except Exception as e:
                print(f"Error updating metadata for folder rename: {str(e)}")
        
        # Process the new folder
        self.process_folder(new_folder)

    def on_modified(self, event):
        if not event.is_directory:
            return
        # Only process if enough time has passed since last update
        current_time = time.time()
        if current_time - self.last_update > 2:  # 2 seconds delay
            folder_name = os.path.basename(event.src_path)
            self.process_folder(folder_name)
            self.last_update = current_time

def start_watcher(base_dir):
    print("Starting song folder watcher...")
    print("Use 'python watch_songs.py stop' to stop")
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Watch song folders for changes')
    parser.add_argument('command', choices=['start', 'stop'], help='Command to execute')
    parser.add_argument('--base-dir', default='.', help='Base directory to watch')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_watcher(args.base_dir)
    elif args.command == 'stop':
        stop_watcher()

if __name__ == "__main__":
    main()
