#!/usr/bin/env python3
import os
import yaml
from typing import Dict
import logging
import sys
from normalize_new_song import normalize_title

def normalize_song_tags(base_dir: str) -> None:
    """
    Normalize all song keys in song_tags.yml to match the folder naming convention
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('normalize_song_tags.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Load existing song tags
        with open("song_tags.yml", "r") as f:
            tags = yaml.safe_load(f)
            
        # Create a mapping of old to new keys
        updates = []
        for old_key in list(tags["songs"]):  # Use list to avoid modifying while iterating
            data = tags["songs"][old_key]
            
            # Get the normalized key
            if "actual_title" in data:
                # Use actual_title if available
                normalized_key = normalize_title(data["actual_title"])
            else:
                # Fall back to the current key
                normalized_key = normalize_title(old_key)
            
            # Skip if already normalized
            if old_key.lower() == normalized_key:
                continue
            
            # Add to updates
            updates.append((old_key, normalized_key))
        
        # Apply the updates
        for old_key, new_key in updates:
            data = tags["songs"][old_key]
            tags["songs"][new_key] = data
            del tags["songs"][old_key]
            logging.info(f"Updated song_tags.yml: {old_key} -> {new_key}")
        
        # Write updated tags
        with open("song_tags.yml", "w") as f:
            yaml.dump(tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
        logging.info("Successfully normalized all song keys in song_tags.yml")
        
    except Exception as e:
        logging.error(f"Error in normalize_song_tags: {str(e)}")
        raise

def main():
    """Main function to normalize song tags."""
    normalize_song_tags(".")

if __name__ == "__main__":
    main()
