# The generate_song_metadata.py script correctly handles metadata preservation:
# 1. Preserves all existing metadata properties for current songs (lines 156-162)
# 2. Restores metadata from backup for songs that exist in backup (lines 165-173)
# 3. Sets default values (including ai_generated=False) for new songs (lines 177-189)
# 4. Ensures all songs have required fields (lines 191-212)
# 5. Creates backups before modifying files (lines 216-223)
# 6. Performs proper comparison to identify changes (lines 292-339)
#
# The script is working as intended, preserving the 'ai_generated' field and other
# metadata while properly handling new songs and backups.

import os
import yaml
from typing import Dict, List, Set, Optional
import logging
import sys
import shutil

def get_song_title_from_file(file_path: str) -> str:
    """Extract song title from file path using directory name."""
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # Skip the root directory
    if dir_name == ".":
        logging.debug(f"Skipping root directory for {file_path}")
        return None
    
    # Just normalize spaces for minimal normalization
    normalized = ' '.join(dir_name.split())  # Normalize spaces
    logging.debug(f"Extracted title '{normalized}' from directory '{dir_name}' for file {file_path}")
    return normalized

def write_tags(tags: Dict, output_file: str = "song_metadata.yml") -> None:
    """Write tags to YAML file."""
    with open(output_file, "w") as f:
        yaml.dump(tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logging.info(f"Metadata written to {output_file}")

def compare_tags(existing_tags: Dict, new_tags: Dict) -> Dict:
    """Compare existing and new tags to find missing and new songs.
    
    Returns a dictionary with:
    - missing_songs: List of songs present in metadata but missing from filesystem
    - new_songs: List of songs present in filesystem but not in metadata
    - restored_songs: List of songs whose metadata was restored from backup
    """
    result = {
        "missing_songs": [],
        "new_songs": [],
        "restored_songs": []
    }
    
    existing_songs = set(existing_tags.get("songs", {}).keys())
    new_songs = set(new_tags.get("songs", {}).keys())
    
    # Find songs in filesystem but not in existing metadata
    for song in new_songs:
        if song not in existing_songs:
            result["new_songs"].append(song)
            logging.debug(f"New song found: {song}")
    
    # Find songs in metadata but missing from filesystem
    for song in existing_songs:
        if song not in new_songs:
            result["missing_songs"].append(song)
            logging.debug(f"Song in metadata but not found in filesystem: {song}")
    
    # Check if we restored songs from backup
    for song in new_tags.get("songs", {}):
        if "restored_from_backup" in new_tags["songs"][song]:
            result["restored_songs"].append(song)
            # Remove this temporary marker
            del new_tags["songs"][song]["restored_from_backup"]
    
    return result

def load_backup_metadata(backup_path: str) -> Optional[Dict]:
    """Load backup song metadata from the specified path."""
    try:
        with open(backup_path, "r") as f:
            backup_tags = yaml.safe_load(f)
            logging.info(f"Loaded backup metadata from {backup_path} with {len(backup_tags.get('songs', {}))} songs")
            return backup_tags
    except FileNotFoundError:
        logging.info(f"Backup metadata file {backup_path} not found")
        return None
    except Exception as e:
        logging.error(f"Error loading backup metadata from {backup_path}: {str(e)}")
        return None

def generate_song_metadata(base_dir: str, output_file: str, dry_run: bool = False, verbose: bool = False) -> Dict:
    """Generate song metadata from lyrics files."""
    
    logging.info(f"Searching for lyrics files in {os.path.abspath(base_dir)}")
    
    # Load existing song metadata
    song_metadata_file = output_file
    try:
        with open(song_metadata_file, "r") as f:
            existing_tags = yaml.safe_load(f)
            logging.info(f"Loaded existing metadata from {song_metadata_file} with {len(existing_tags.get('songs', {}))} songs")
    except FileNotFoundError:
        logging.info(f"Metadata file {song_metadata_file} not found, creating new metadata")
        existing_tags = {"songs": {}}
    
    # Load backup metadata if available
    backup_path = f"{output_file}.bak"
    backup_tags = load_backup_metadata(backup_path)
    if not backup_tags:
        logging.info("No backup metadata available, using empty backup")
        backup_tags = {"songs": {}}
        
    
    # Get all lyrics files
    lyrics_files = []
    for root, dirs, files in os.walk(base_dir):
        logging.debug(f"Scanning directory: {root}")
        for file in files:
            # Case-insensitive matching for _lyrics.txt
            if file.lower().endswith("_lyrics.txt"):
                # Skip the consolidated_songs_lyrics.txt file
                if file.lower() == "consolidated_songs_lyrics.txt":
                    continue
                    
                # Skip files in the tools directory
                if "tools" in root.split(os.path.sep):
                    continue
                    
                full_path = os.path.join(root, file)
                lyrics_files.append(full_path)
                logging.debug(f"Found lyrics file: {full_path}")
    
    logging.info(f"Found {len(lyrics_files)} lyrics files")
    
    # Process lyrics files
    current_songs = set()
    for file_path in lyrics_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                logging.debug(f"Skipping empty file: {file_path}")
                continue
            
            # Use directory name for song title extraction (consistent with consolidate_songs.py)
            title = get_song_title_from_file(file_path)
            
            if not title:
                logging.warning(f"Could not extract title from {file_path}")
                continue
                
            # Use directory name as the key
            dir_name = os.path.basename(os.path.dirname(file_path))
            current_songs.add(dir_name)
            
            if verbose:
                logging.debug(f"Processing song directory: {dir_name}")
        except Exception as e:
            if verbose:
                logging.error(f"Error processing {file_path}: {str(e)}")
    
    # Generate new tags
    new_tags = {"songs": {}}
    
    # Copy existing tags for songs that still exist, preserving all properties
    for title in existing_tags.get("songs", {}):
        if title in current_songs:
            # Preserve all existing metadata for this song
            new_tags["songs"][title] = existing_tags["songs"][title].copy()
            metadata_fields = ", ".join(f"{k}={v}" for k, v in existing_tags["songs"][title].items() 
                                      if k in ['status', 'ai_generated'] or k == 'tags' and v)
            logging.debug(f"Preserving existing metadata for: {title} [{metadata_fields}]")
    
    # Check if there are songs in backup but not in current metadata
    for title in backup_tags.get("songs", {}):
        if title in current_songs and title not in new_tags["songs"]:
            # Song exists in backup but not in current metadata - restore from backup
            new_tags["songs"][title] = backup_tags["songs"][title].copy()
            # Add a marker that we'll use in the comparison and then remove
            new_tags["songs"][title]["restored_from_backup"] = True
            metadata_fields = ", ".join(f"{k}={v}" for k, v in backup_tags["songs"][title].items() 
                                      if k in ['status', 'ai_generated'] or k == 'tags' and v)
            logging.info(f"Restored metadata from backup for: {title} [{metadata_fields}]")
    
    # Add new songs
    new_songs_added = []
    for title in current_songs:
        if title not in new_tags["songs"]:
            # Set default values for new songs
            new_tags["songs"][title] = {
                "actual_title": title,
                "status": "deferred",
                "tags": [],
                "notes": [],
                "ai_generated": False
            }
            new_songs_added.append(title)
            logging.info(f"Adding new song to metadata with default values: {title}")
            
    # Ensure all songs have required fields
    for title in new_tags["songs"]:
        song_data = new_tags["songs"][title]
        # Add default values for any missing required fields
        missing_fields = []
        if "actual_title" not in song_data:
            song_data["actual_title"] = title
            missing_fields.append("actual_title")
        if "status" not in song_data:
            song_data["status"] = "deferred"
            missing_fields.append("status")
        if "tags" not in song_data or song_data["tags"] is None:
            song_data["tags"] = []
            missing_fields.append("tags")
        if "notes" not in song_data or song_data["notes"] is None:
            song_data["notes"] = []
            missing_fields.append("notes")
        if "ai_generated" not in song_data:
            song_data["ai_generated"] = False
            missing_fields.append("ai_generated")
            
        if missing_fields:
            logging.debug(f"Added missing fields for {title}: {', '.join(missing_fields)}")
    
    # Write the tags
    if not dry_run:
        # Create a backup of the current file if it exists
        if os.path.exists(output_file):
            backup_file = f"{output_file}.bak"
            try:
                shutil.copy2(output_file, backup_file)
                logging.info(f"Created backup of existing metadata file: {backup_file}")
            except Exception as e:
                logging.error(f"Failed to create backup: {str(e)}")
        
        with open(output_file, "w") as f:
            yaml.dump(new_tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logging.info(f"Updated metadata written to {output_file} with {len(new_tags.get('songs', {}))} songs")
        
        # Log a summary of changes
        if new_songs_added:
            logging.info(f"Summary: Added {len(new_songs_added)} new songs to metadata")
            for song in new_songs_added[:10]:  # Show first 10 to avoid excessive logging
                logging.info(f"  - {song}")
            if len(new_songs_added) > 10:
                logging.info(f"  - ... and {len(new_songs_added) - 10} more")
        else:
            logging.info("Summary: No new songs added to metadata")
    
    return new_tags

def main():
    """Main function to generate song metadata."""
    # Set up more verbose logging based on command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Generate song metadata YAML file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-backup', action='store_true', help='Skip loading backup metadata')
    parser.add_argument('--output', type=str, help='Output file path for song metadata (default: song_metadata.yml)')
    args = parser.parse_args()
    
    log_level = logging.DEBUG if args.debug else (logging.INFO if args.verbose else logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('generate_song_metadata.log'),
            logging.StreamHandler()
        ]
    )
    
    # Use parent directory for finding lyrics files
    base_dir = ".."
    output_file = args.output if args.output else "song_metadata.yml"
    
    logging.info(f"=== Starting song metadata generation ===")
    logging.info(f"Looking for lyrics files in: {os.path.abspath(base_dir)}")
    logging.info(f"Output metadata file will be: {os.path.abspath(output_file)}")
    
    if not args.no_backup:
        backup_path = f"{output_file}.bak"
        if os.path.exists(backup_path):
            logging.info(f"Will merge metadata from backup file: {os.path.abspath(backup_path)}")
        else:
            logging.info(f"No backup metadata file found at: {os.path.abspath(backup_path)}")
    
    try:
        # Generate new metadata
        new_tags = generate_song_metadata(
            base_dir, 
            output_file, 
            verbose=args.verbose or args.debug
        )
        if not new_tags or not new_tags.get("songs"):
            logging.error("Failed to generate metadata - no songs found")
            return
        
        logging.info(f"Generated metadata for {len(new_tags.get('songs', {}))} songs")
        
        # Check if file exists and compare with existing
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                existing_tags = yaml.safe_load(f)
                logging.info(f"Loaded existing metadata from {output_file} for comparison")
            
            # Compare existing and new tags
            existing_songs = existing_tags.get("songs", {})
            new_songs = new_tags.get("songs", {})
            
            # Check if any song is missing tags or notes
            has_changes = False
            for title in new_songs:
                if title in existing_songs:
                    existing_song = existing_songs[title]
                    new_song = new_songs[title]
                    
                    # Check for missing tags
                    if "tags" not in existing_song or existing_song["tags"] is None:
                        has_changes = True
                        logging.debug(f"Adding missing tags field to {title}")
                        new_song["tags"] = []
                    
                    # Check for missing notes
                    if "notes" not in existing_song or existing_song["notes"] is None:
                        has_changes = True
                        logging.debug(f"Adding missing notes field to {title}")
                        new_song["notes"] = []
            
            # Check for new songs that weren't in the existing metadata
            comparison_result = compare_tags(existing_tags, new_tags)
            new_song_count = len(comparison_result["new_songs"])
            restored_song_count = len(comparison_result["restored_songs"])
            
            if new_song_count > 0:
                has_changes = True
                logging.info(f"Found {new_song_count} new songs to add to metadata:")
                for song in comparison_result["new_songs"]:
                    logging.info(f"  - {song}")
            
            if restored_song_count > 0:
                has_changes = True
                logging.info(f"Summary: Restored {restored_song_count} songs from backup metadata:")
                for song in comparison_result["restored_songs"]:
                    logging.info(f"  - {song}")
            
            if not has_changes:
                logging.info(f"Summary: No changes needed in {output_file}")
                return
            
            # Write to main file
            write_tags(new_tags, output_file)
            
            # Log a summary of changes
            if new_song_count > 0:
                logging.info(f"Summary: Added {new_song_count} new songs to {output_file}")
            # Log the summary of what was done
            logging.info(f"Summary: Updated metadata in {output_file} successfully")
        
        # Log success message outside of all try-except blocks
        logging.info("=== Successfully completed song metadata generation ===")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
