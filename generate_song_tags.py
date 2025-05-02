import os
import yaml
from typing import Dict, List
import logging
import sys

def get_song_title_from_file(file_path: str) -> str:
    """Extract song title from file path by removing '_lyrics.txt' suffix."""
    base_name = os.path.basename(file_path)
    return base_name.replace("_lyrics.txt", "").replace("-", " ").title()

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
    
    for file_path in lyrics_files:
        title = get_song_title_from_file(file_path)
        
        # Check if song exists in existing tags
        if title in existing_tags["songs"]:
            new_tags["songs"][title] = existing_tags["songs"][title]
        else:
            # Generate default tags based on existing pattern
            new_tags["songs"][title] = {
                "status": "deferred",
                "date": "",
                "album": ""
            }
    
    return new_tags

def write_test_file(new_tags: Dict, test_file: str = "test_song_tags.yml"):
    """Write the generated tags to a test file."""
    with open(test_file, "w") as f:
        yaml.dump(new_tags, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def compare_tags(existing_tags: Dict, new_tags: Dict) -> List[str]:
    """Compare existing tags with new tags and return list of missing songs."""
    existing_songs = set(existing_tags["songs"]) if "songs" in existing_tags else set()
    new_songs = set(new_tags["songs"]) if "songs" in new_tags else set()
    
    # Songs in new tags but not in existing
    missing_songs = new_songs - existing_songs
    return list(missing_songs)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('generate_song_tags.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Generate new tags
        new_tags = generate_song_tags(".")
        logging.info("Successfully generated new song tags")
        
        # Write to test file
        write_test_file(new_tags)
        logging.info("Successfully wrote test file")
        
        # Load existing tags for comparison
        with open("song_tags.yml", "r") as f:
            existing_tags = yaml.safe_load(f)
        
        # Find missing songs
        missing_songs = compare_tags(existing_tags, new_tags)
        
        print(f"\nGenerated test file: test_song_tags.yml")
        print(f"\nSongs in lyrics files but missing from song_tags.yml:")
        for song in missing_songs:
            print(f"- {song}")
            logging.info(f"Missing song: {song}")
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        sys.exit(1)
