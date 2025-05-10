#!/usr/bin/env python3
import os
import yaml
from typing import Dict
import logging

def get_song_title_from_file(file_path: str) -> str:
    """Extract song title from file path using directory name."""
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # Skip the root directory
    if dir_name == ".":
        return None
    
    return dir_name

def capture_song_titles(base_dir: str) -> Dict:
    """
    Capture song titles from folder names and store them in song_tags.yml
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('capture_song_titles.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Load existing song tags
        with open("song_tags.yml", "r") as f:
            existing_tags = yaml.safe_load(f)
            
        # Get all lyrics files
        lyrics_files = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith("_lyrics.txt"):
                    lyrics_files.append(os.path.join(root, file))
        
        # Get current song titles from lyrics files
        current_songs = {}
        for file_path in lyrics_files:
            title = get_song_title_from_file(file_path)
            if title is not None:  # Skip root directory
                current_songs[title] = title
        
        # Update existing tags with the actual titles
        for title in existing_tags["songs"]:
            if title in current_songs:
                existing_tags["songs"][title]["actual_title"] = current_songs[title]
                logging.info(f"Added actual title for {title}: {current_songs[title]}")
        
        # Write updated tags
        with open("song_tags.yml", "w") as f:
            yaml.dump(existing_tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
        logging.info("Successfully captured song titles and updated song_tags.yml")
        
    except Exception as e:
        logging.error(f"Error in capture_song_titles: {str(e)}")
        raise

def main():
    """Main function to capture song titles."""
    capture_song_titles(".")

if __name__ == "__main__":
    main()
