#!/usr/bin/env python3
import yaml
from typing import Dict
import os

def update_metadata():
    # Load existing metadata
    metadata_file = "song_metadata.yml"
    with open(metadata_file, "r") as f:
        metadata = yaml.safe_load(f)
        
    # Add Flickering Candle metadata
    flickering_candle_data = {
        "tags": [],
        "date": None,
        "notes": [],
        "status": "released",
        "actual_title": "Flickering Candle"
    }
    
    # Update metadata
    metadata["songs"]["flickering-candle"] = flickering_candle_data
    
    # Backup existing file
    backup_file = metadata_file + ".bak"
    os.replace(metadata_file, backup_file)
    
    # Save updated metadata
    with open(metadata_file, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False)
    
    print(f"Updated {metadata_file} with Flickering Candle metadata")
    print(f"Backup created at {backup_file}")

if __name__ == "__main__":
    update_metadata()
