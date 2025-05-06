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
    
    # Check for hyphens and log as error
    if '-' in dir_name:
        logging.error(f"Directory name contains hyphen: {dir_name}")
        return None
    
    # Normalize spaces and case for matching
    normalized = ' '.join(dir_name.split())  # Normalize spaces
    return normalized

def generate_song_tags(base_dir: str) -> Dict:
    """
    Generate song tags for all _lyrics.txt files in the directory.
    Follows the pattern from existing song_tags.yml.
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
    
    # Generate new tags
    new_tags = {"songs": {}, "albums": existing_tags.get("albums", {})}
    
    # Process all current songs
    for file_path in lyrics_files:
        title = get_song_title_from_file(file_path)
        if title is None:  # Skip root directory
            continue
        
        # Check if song exists in existing tags
        if title in existing_tags["songs"]:
            # Copy existing tags for this song
            new_tags["songs"][title] = existing_tags["songs"][title]
        else:
            # Create new tags for this song
            new_tags["songs"][title] = {
                "tags": [],
                "albums": [],
                "artists": [],
                "year": None,
                "notes": []
            }
    
    # Remove songs that no longer exist
    for title in existing_tags["songs"]:
        if title not in new_tags["songs"]:
            logging.info(f"Removing deleted song from tags: {title}")
    
    return new_tags

def write_test_file(new_tags: Dict, test_file: str = "test_song_tags.yml"):
    """Write the generated tags to a test file."""
    with open(test_file, "w") as f:
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
        format='%(asctime)s - %(levelname)s - %(message)s',
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
        
        # Write to test file
        write_test_file(new_tags)
        
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
        
        # Log any directories that were skipped due to hyphens
        with open('generate_song_tags.log', 'r') as f:
            log_content = f.read()
        hyphen_logs = [line.split(': ')[1] for line in log_content.split('\n') 
                      if 'Directory name contains hyphen' in line]
        if hyphen_logs:
            logging.info("\nDirectories skipped due to hyphenated names:")
            for log in hyphen_logs:
                logging.info(f"- {log}")
        
        logging.info("\nSuccessfully completed song tag generation")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
