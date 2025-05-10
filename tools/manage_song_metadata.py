#!/usr/bin/env python3
import os
import yaml
from typing import Dict, List, Optional
import logging
import sys
import signal
import readline
from normalize_new_song import normalize_title

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print("\n\nExiting gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # Handle termination signal

class SimpleCompleter:
    """Simple autocomplete for song titles."""
    def __init__(self, songs: List[str]):
        self.songs = songs
        
    def complete(self, text, state):
        """Return the next possible completion for text."""
        if state == 0:
            if text:
                self.matches = [s for s in self.songs if s.startswith(text)]
            else:
                self.matches = self.songs[:]

        try:
            return self.matches[state]
        except IndexError:
            return None

class SongMetadataManager:
    def __init__(self, base_dir: str):
        """Initialize the song metadata manager."""
        self.base_dir = base_dir
        self.tags_file = os.path.join(base_dir, "song_metadata.yml")
        self.tags = self._load_tags()
        
    def _load_tags(self) -> Dict:
        """Load song metadata from file."""
        try:
            with open(self.tags_file, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"songs": {}}
            
    def _save_tags(self) -> None:
        """Save song metadata to file."""
        with open(self.tags_file, "w") as f:
            yaml.dump(self.tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
    def _get_song_list(self) -> List[str]:
        """Get a list of all songs."""
        return list(self.tags["songs"].keys())
        
    def _get_song_data(self, song_key: str) -> Dict:
        """Get data for a specific song."""
        return self.tags["songs"].get(song_key, {})
        
    def _normalize_song_key(self, title: str) -> str:
        """Normalize a song title to a consistent format."""
        return normalize_title(title)
        
    def _print_menu(self) -> None:
        """Print the main menu."""
        print("\nSong Metadata Management Menu:")
        print("1. List all songs")
        print("2. Add new song")
        print("3. Update song metadata")
        print("4. Delete song")
        print("5. Rename song")
        print("6. Exit")
        
    def _get_choice(self, prompt: str, choices: List[str]) -> str:
        """Get user choice from a list of options with autocomplete."""
        while True:
            print(f"\n{prompt}")
            print("Type to autocomplete or enter a number:")
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice}")
            
            try:
                # Set up readline completer
                completer = SimpleCompleter(choices)
                readline.set_completer(completer.complete)
                readline.parse_and_bind('tab: complete')
                
                # Get input
                choice = input("Enter choice (number or type to autocomplete): ").strip()
                
                # Try to convert to number first
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(choices):
                        return choices[choice_num - 1]
                except ValueError:
                    # If not a number, check if it's a complete song title
                    if choice in choices:
                        return choice
                    
                    # If not found, show error
                    print("Invalid choice. Please try again.")
            except EOFError:
                print("\nExiting...")
                sys.exit(0)
                
    def _get_song_key(self, prompt: str) -> str:
        """Get a normalized song key from user input."""
        while True:
            title = input(f"\n{prompt}: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
                
            normalized = self._normalize_song_key(title)
            print(f"Normalized key: {normalized}")
            
            confirm = input("Confirm this key? (y/n): ").lower()
            if confirm == 'y':
                return normalized
            elif confirm == 'n':
                continue
            else:
                print("Invalid input. Please try again.")
                
    def _get_metadata(self, existing_data: Dict = None) -> Dict:
        """Get metadata for a song."""
        if existing_data is None:
            existing_data = {}
            
        metadata = {}
        
        # Use the original title as the actual title
        if "actual_title" not in existing_data:
            metadata["actual_title"] = input("\nEnter the song title: ").strip()
        else:
            metadata["actual_title"] = existing_data["actual_title"]
            
        # Get tags
        if "tags" in existing_data:
            metadata["tags"] = existing_data["tags"]
        else:
            metadata["tags"] = []
            
        print("\nCurrent tags:", ", ".join(metadata["tags"]) if metadata["tags"] else "None")
        add_tag = input("Add a new tag? (y/n): ").lower()
        while add_tag == 'y':
            tag = input("Enter new tag: ").strip()
            if tag and tag not in metadata["tags"]:
                metadata["tags"].append(tag)
            add_tag = input("Add another tag? (y/n): ").lower()
            
        # Get status
        valid_statuses = ["released", "deferred", "in_progress", "draft"]
        if "status" in existing_data:
            default_status = existing_data["status"]
        else:
            default_status = "deferred"
            
        status = self._get_choice("\nSelect status", valid_statuses)
        metadata["status"] = status
        
        # Get notes
        if "notes" in existing_data:
            metadata["notes"] = existing_data["notes"]
        else:
            metadata["notes"] = []
            
        print("\nCurrent notes:", ", ".join(metadata["notes"]) if metadata["notes"] else "None")
        add_note = input("Add a new note? (y/n): ").lower()
        while add_note == 'y':
            note = input("Enter new note: ").strip()
            if note and note not in metadata["notes"]:
                metadata["notes"].append(note)
            add_note = input("Add another note? (y/n): ").lower()
            
        return metadata
        
    def list_songs(self) -> None:
        """List all songs with their metadata."""
        print("\nAll Songs:")
        for song_key in self._get_song_list():
            data = self._get_song_data(song_key)
            print(f"\n{song_key}")
            print(f"Actual Title: {data.get('actual_title', 'N/A')}")
            print(f"Status: {data.get('status', 'N/A')}")
            print(f"Tags: {', '.join(data.get('tags', []))}")
            print(f"Notes: {', '.join(data.get('notes', []))}")
            
    def add_song(self) -> None:
        """Add a new song."""
        print("\nAdding new song...")
        
        # Get the song title
        title = input("\nEnter the song title: ").strip()
        if not title:
            print("Title cannot be empty.")
            return
            
        # Normalize the title
        normalized = self._normalize_song_key(title)
        print(f"\nNormalized folder name: {normalized}")
        
        # Confirm the normalized title
        confirm = input("Confirm this folder name? (y/n): ").lower()
        if confirm != 'y':
            return
            
        # Check if song already exists
        if normalized in self.tags["songs"]:
            print(f"\nError: Song '{normalized}' already exists.")
            return
            
        # Create the folder
        folder_path = os.path.join(self.base_dir, normalized)
        if os.path.exists(folder_path):
            print(f"\nError: Folder '{folder_path}' already exists.")
            return
            
        os.makedirs(folder_path)
        print(f"\nCreated folder: {folder_path}")
        
        # Create lyrics file
        lyrics_file = os.path.join(folder_path, f"{normalized}_lyrics.txt")
        with open(lyrics_file, "w") as f:
            f.write(f"{title}\n\n")  # Write the original title as the first line
        print(f"Created lyrics file: {lyrics_file}")
        
        # Create metadata with the title
        metadata = {
            "actual_title": title,
            "tags": [],
            "status": "deferred",
            "notes": []
        }
        
        # Get additional metadata (tags, status, notes)
        metadata.update(self._get_metadata(metadata))
        
        self.tags["songs"][normalized] = metadata
        self._save_tags()
        print(f"\nSuccessfully added song: {normalized}")
        
    def update_song(self) -> None:
        """Update an existing song's metadata."""
        songs = self._get_song_list()
        if not songs:
            print("\nNo songs found!")
            return
            
        song_key = self._get_choice("\nSelect song to update", songs)
        existing_data = self._get_song_data(song_key)
        
        # Get folder path
        folder_path = os.path.join(self.base_dir, song_key)
        if not os.path.exists(folder_path):
            print(f"\nWarning: Folder '{folder_path}' not found.")
            
        # Check lyrics file
        lyrics_file = os.path.join(folder_path, f"{song_key}_lyrics.txt")
        if not os.path.exists(lyrics_file):
            print(f"\nWarning: Lyrics file '{os.path.basename(lyrics_file)}' not found.")
            
        print("\nCurrent Metadata:")
        print(f"Actual Title: {existing_data.get('actual_title', 'N/A')}")
        print(f"Status: {existing_data.get('status', 'N/A')}")
        print(f"Tags: {', '.join(existing_data.get('tags', []))}")
        print(f"Notes: {', '.join(existing_data.get('notes', []))}")
        
        confirm = input("\nUpdate this song? (y/n): ").lower()
        if confirm == 'y':
            metadata = self._get_metadata(existing_data)
            self.tags["songs"][song_key] = metadata
            self._save_tags()
            
            # Ask if user wants to update lyrics
            update_lyrics = input("\nUpdate lyrics file? (y/n): ").lower()
            if update_lyrics == 'y':
                try:
                    with open(lyrics_file, "r") as f:
                        lyrics = f.read()
                    print(f"\nCurrent lyrics:\n{lyrics}")
                    
                    new_lyrics = input("\nEnter new lyrics (press Enter to keep current): ").strip()
                    if new_lyrics:
                        with open(lyrics_file, "w") as f:
                            f.write(new_lyrics)
                        print(f"\nUpdated lyrics file: {os.path.basename(lyrics_file)}")
                except Exception as e:
                    print(f"\nError updating lyrics: {str(e)}")
            
            print(f"\nSuccessfully updated song: {song_key}")
        
    def delete_song(self) -> None:
        """Delete an existing song."""
        songs = self._get_song_list()
        if not songs:
            print("\nNo songs found!")
            return
            
        song_key = self._get_choice("\nSelect song to delete", songs)
        
        # Get folder path
        folder_path = os.path.join(self.base_dir, song_key)
        if not os.path.exists(folder_path):
            print(f"\nWarning: Folder '{folder_path}' not found.")
            
        confirm = input(f"\nAre you sure you want to delete '{song_key}'? (y/n): ").lower()
        if confirm == 'y':
            # Delete folder and its contents
            if os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                print(f"\nDeleted folder: {folder_path}")
            
            # Delete metadata
            del self.tags["songs"][song_key]
            self._save_tags()
            print(f"\nSuccessfully deleted song: {song_key}")
        
    def rename_song(self) -> None:
        """Rename an existing song."""
        songs = self._get_song_list()
        if not songs:
            print("\nNo songs found!")
            return
            
        old_key = self._get_choice("\nSelect song to rename", songs)
        new_key = self._get_song_key("Enter new song title")
        
        if new_key in self.tags["songs"]:
            print(f"\nError: Song '{new_key}' already exists.")
            return
            
        # Get folder paths
        old_folder = os.path.join(self.base_dir, old_key)
        new_folder = os.path.join(self.base_dir, new_key)
        
        if not os.path.exists(old_folder):
            print(f"\nWarning: Folder '{old_folder}' not found.")
            
        confirm = input(f"\nRename '{old_key}' to '{new_key}'? (y/n): ").lower()
        if confirm == 'y':
            # Rename folder
            if os.path.exists(old_folder):
                import shutil
                if os.path.exists(new_folder):
                    print(f"\nError: Folder '{new_folder}' already exists.")
                    return
                
                # Move folder contents
                shutil.move(old_folder, new_folder)
                print(f"\nRenamed folder: {old_folder} -> {new_folder}")
            
            # Update metadata
            self.tags["songs"][new_key] = self.tags["songs"][old_key]
            del self.tags["songs"][old_key]
            self._save_tags()
            print(f"\nSuccessfully renamed song: {old_key} -> {new_key}")
            
    def run(self) -> None:
        """Run the main menu loop."""
        while True:
            self._print_menu()
            try:
                choice = int(input("\nEnter your choice (1-6): "))
                if choice == 1:
                    self.list_songs()
                elif choice == 2:
                    self.add_song()
                elif choice == 3:
                    self.update_song()
                elif choice == 4:
                    self.delete_song()
                elif choice == 5:
                    self.rename_song()
                elif choice == 6:
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid choice. Please try again.")
            except ValueError:
                print("\nPlease enter a number.")
                
if __name__ == "__main__":
    manager = SongMetadataManager(".")
    manager.run()
