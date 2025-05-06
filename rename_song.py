#!/usr/bin/env python3

import os
import yaml
import logging
import sys
from pathlib import Path


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rename_song.log'),
            logging.StreamHandler()
        ]
    )

def load_yaml_file(file_path: str) -> dict:
    """Load a YAML file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        sys.exit(1)

def save_yaml_file(data: dict, file_path: str):
    """Save data to a YAML file."""
    try:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    except Exception as e:
        logging.error(f"Error saving {file_path}: {str(e)}")
        sys.exit(1)

def update_song_title(file_path: str, old_title: str, new_title: str):
    """Update a song title in a YAML file."""
    data = load_yaml_file(file_path)
    
    if "songs" in data:
        if old_title in data["songs"]:
            data["songs"][new_title] = data["songs"][old_title]
            del data["songs"][old_title]
            save_yaml_file(data, file_path)
            logging.info(f"Updated title in {file_path}: {old_title} -> {new_title}")
        else:
            logging.warning(f"Old title '{old_title}' not found in {file_path}")
    else:
        logging.warning(f"No songs section found in {file_path}")

def rename_song_directory(old_dir: str, new_dir: str):
    """Rename a song directory and update YAML files."""
    try:
        # Get absolute paths
        old_path = Path(old_dir)
        new_path = Path(new_dir)
        
        # Rename directory
        old_path.rename(new_path)
        logging.info(f"Renamed directory: {old_path} -> {new_path}")
        
        # Update YAML files
        update_song_title("song_tags.yml", old_dir, new_dir)
        update_song_title("consolidated_songs.yml", old_dir, new_dir)
        
        logging.info("Successfully completed directory rename and YAML updates")
        
    except Exception as e:
        logging.error(f"Error during directory rename: {str(e)}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments and execute rename."""
    if len(sys.argv) != 3:
        print("Usage: python rename_song.py <old_directory_name> <new_directory_name>")
        sys.exit(1)
    
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    
    setup_logging()
    rename_song_directory(old_dir, new_dir)

if __name__ == "__main__":
    main()
