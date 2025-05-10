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
    """
    # Remove special characters except hyphens
    normalized = ''.join(c if c.isalnum() or c == '-' or c == ' ' else '' for c in title)
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

def rename_song_folders(base_dir: str) -> Dict:
    """
    Rename all song folders to a consistent format and update song_tags.yml
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('normalize_song_folders.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Load existing song tags
        with open("song_tags.yml", "r") as f:
            existing_tags = yaml.safe_load(f)
            
        # Get all song folders
        song_folders = {}
        for root, dirs, files in os.walk(base_dir):
            for dir_name in dirs:
                # Skip root directory and .git
                if dir_name in [".", "..", ".git"]:
                    continue
                
                # Get the full path
                full_path = os.path.join(root, dir_name)
                
                # Normalize the title
                normalized = normalize_title(dir_name)
                
                # Skip if already normalized
                if dir_name.lower() == normalized:
                    continue
                
                # Add to list of folders to rename
                song_folders[full_path] = normalized
        
        # Rename folders
        for old_path, new_name in song_folders.items():
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            # Check if new folder already exists
            if os.path.exists(new_path):
                logging.warning(f"New folder {new_name} already exists, skipping {old_path}")
                continue
            
            try:
                os.rename(old_path, new_path)
                logging.info(f"Renamed {old_path} to {new_path}")
            except Exception as e:
                logging.error(f"Error renaming {old_path}: {str(e)}")
                continue
        
        # Update song_tags.yml with new folder names
        # First create a list of updates to make
        updates = []
        for title, data in existing_tags["songs"].items():
            if "actual_title" in data:
                normalized = normalize_title(data["actual_title"])
                if normalized != title.lower():
                    updates.append((title, normalized))
        
        # Then apply the updates
        for old_title, new_title in updates:
            data = existing_tags["songs"][old_title]
            existing_tags["songs"][new_title] = data
            del existing_tags["songs"][old_title]
            logging.info(f"Updated song_tags.yml: {old_title} -> {new_title}")
        
        # Write updated tags
        with open("song_tags.yml", "w") as f:
            yaml.dump(existing_tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
        logging.info("Successfully normalized all song folders and updated song_tags.yml")
        
    except Exception as e:
        logging.error(f"Error in rename_song_folders: {str(e)}")
        raise

def main():
    """Main function to rename song folders."""
    rename_song_folders(".")

if __name__ == "__main__":
    main()
