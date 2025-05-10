#!/usr/bin/env python3
import os
import yaml
from typing import Dict
import logging
import sys

def normalize_title(title: str) -> str:
    """
    Normalize a song title to a consistent format:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters except hyphens
    - Remove leading/trailing hyphens
    - Handle Unicode characters properly
    """
    import unicodedata
    
    # Normalize Unicode characters (NFKD form)
    normalized = unicodedata.normalize('NFKD', title)
    # Remove combining characters (accents, etc.)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    # Remove special characters except hyphens
    normalized = ''.join(c if c.isalnum() or c == '-' or c == ' ' else '' for c in normalized)
    # Convert to lowercase
    normalized = normalized.lower()
    # Replace spaces with hyphens
    normalized = normalized.replace(' ', '-')
    # Remove multiple consecutive hyphens
    while '--' in normalized:
        normalized = normalized.replace('--', '-')
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    return normalized

def normalize_new_song(base_dir: str, song_dir: str) -> None:
    """
    Normalize a new song folder name and update song_tags.yml
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('normalize_new_song.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Get the full path to the song directory
        full_path = os.path.join(base_dir, song_dir)
        
        # Normalize the title
        normalized = normalize_title(song_dir)
        
        # Skip if already normalized
        if song_dir.lower() == normalized:
            logging.info(f"Folder name {song_dir} is already normalized")
            return
        
        # Get the new path
        new_path = os.path.join(base_dir, normalized)
        
        # Check if new folder already exists
        if os.path.exists(new_path):
            logging.warning(f"New folder {new_path} already exists")
            return
        
        # Rename the folder
        os.rename(full_path, new_path)
        logging.info(f"Renamed {full_path} to {new_path}")
        
        # Update song_tags.yml
        with open("song_tags.yml", "r") as f:
            tags = yaml.safe_load(f)
            
        lyrics_file = os.path.join(new_path, f"{os.path.basename(new_path)}_lyrics.txt")
        if os.path.exists(lyrics_file):
            with open(lyrics_file, "r") as f:
                actual_title = f.readline().strip()  # Assume first line is the title
            
            with open("song_metadata.yml", "r") as f:
                tags = yaml.safe_load(f)
            
            if "songs" not in tags:
                tags["songs"] = {}
            
            tags["songs"][normalized] = {
                "actual_title": actual_title,
                "status": "deferred",
                "tags": [],
                "notes": []
            }
            
            with open("song_metadata.yml", "w") as f:
                yaml.dump(tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
            logging.info(f"Updated song_metadata.yml: {song_dir} -> {normalized}")
        
    except Exception as e:
        logging.error(f"Error in normalize_new_song: {str(e)}")
        raise

def main():
    """Main function to normalize a new song folder."""
    if len(sys.argv) != 2:
        print("Usage: python normalize_new_song.py <song_directory>")
        sys.exit(1)
        
    song_dir = sys.argv[1]
    normalize_new_song(".", song_dir)

if __name__ == "__main__":
    main()
