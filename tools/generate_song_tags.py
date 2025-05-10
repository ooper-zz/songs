import os
import yaml
from typing import Dict, List
import logging
import sys

def get_song_title_from_file(file_path: str) -> str:
    """Extract song title from file path using directory name."""
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # Skip the root directory
    if dir_name == ".":
        return None
    
    # Normalize spaces and case for matching
    normalized = ' '.join(dir_name.split())  # Normalize spaces
    return normalized

def generate_song_tags(base_dir: str) -> Dict:
    """
    Generate song tags for all _lyrics.txt files in the directory.
    Focuses on maintaining song metadata without album information.
    """
    existing_tags = {}
    
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
    current_songs = set()
    for file_path in lyrics_files:
        title = get_song_title_from_file(file_path)
        if title is not None:  # Skip root directory
            current_songs.add(title)
    
    # Create new tags structure
    new_tags = {"songs": {}}
    
    # Copy existing tags for songs that still exist
    for title in existing_tags["songs"]:
        if title in current_songs:
            song_data = existing_tags["songs"][title]
            new_tags["songs"][title] = {
                "tags": song_data.get("tags", []),
                "date": song_data.get("date", ""),
                "notes": song_data.get("notes", []),
                "status": song_data.get("status", "deferred")
            }
    
    # Add new songs with default tags
    for title in current_songs:
        if title not in new_tags["songs"]:
            new_tags["songs"][title] = {
                "tags": [],
                "date": "",
                "notes": [],
                "status": "deferred"
            }
    
    return new_tags

def write_tags(new_tags: Dict, target_file: str = "../song_tags.yml"):
    """Write the generated tags to the main song_tags.yml file."""
    with open(target_file, "w") as f:
        yaml.dump(new_tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def compare_tags(existing_tags: Dict, new_tags: Dict) -> List[str]:
    """Compare existing tags with new tags and return list of missing songs."""
    if "songs" not in existing_tags:
        return []
    
    # Get existing song titles (case-insensitive and normalized spaces)
    existing_songs = {title.lower(): title for title in existing_tags["songs"]}
    
    # Get new song titles
    new_songs = set(new_tags["songs"]) if "songs" in new_tags else set()
    
    # Songs in new tags but not in existing (case-insensitive)
    missing_songs = []
    for new_song in new_songs:
        # Normalize spaces and hyphens for comparison
        normalized = ' '.join(new_song.split())
        normalized = normalized.replace('-', ' ')
        if normalized.lower() not in existing_songs:
            missing_songs.append(new_song)
    
    return missing_songs

def main():
    """Main function to generate song tags."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('generate_song_tags.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Generate new tags
        new_tags = generate_song_tags(".")
        if not new_tags:
            logging.error("Failed to generate new tags")
            return
        
        # Check if file exists and compare with existing
        if os.path.exists("song_tags.yml"):
            with open("song_tags.yml", "r") as f:
                existing_tags = yaml.safe_load(f)
            
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
                        logging.info(f"Adding missing tags to {title}")
                        new_song["tags"] = []
                    
                    # Check for missing notes
                    if "notes" not in existing_song or existing_song["notes"] is None:
                        has_changes = True
                        logging.info(f"Adding missing notes to {title}")
                        new_song["notes"] = []
            
            if not has_changes:
                print("No changes detected in song_tags.yml")
                return
            
            # Write to main file
            write_tags(new_tags)
            
            # Load existing tags for comparison
            with open("song_tags.yml", "r") as f:
                existing_tags = yaml.safe_load(f)
            
            # Find missing songs
            missing_songs = compare_tags(existing_tags, new_tags)
            
            # Log missing songs
            if missing_songs:
                logging.info(f"\nSongs in lyrics files but missing from song_tags.yml:")
                for song in missing_songs:
                    logging.info(f"- {song}")
            else:
                logging.info("All songs in lyrics files are present in song_tags.yml")
            
            logging.info("\nSuccessfully completed song tag generation")
        
            existing_tags = yaml.safe_load(f)
        
        # Find missing songs
        missing_songs = compare_tags(existing_tags, new_tags)
        
        # Log missing songs
        if missing_songs:
            logging.info(f"\nSongs in lyrics files but missing from song_tags.yml:")
            for song in missing_songs:
                logging.info(f"- {song}")
        else:
            logging.info("All songs in lyrics files are present in song_tags.yml")
        
        logging.info("\nSuccessfully completed song tag generation")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
