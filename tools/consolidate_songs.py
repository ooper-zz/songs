import os
import yaml
from yaml.representer import SafeRepresenter
import logging
from datetime import datetime
import re

# Track processed versions
processed_versions = {}
import time
try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not installed
    def tqdm(iterable, *args, **kwargs):
        return iterable
import shutil
import argparse
import sys
from pathlib import Path

def find_lyrics_files(base_dir):
    """Find all lyrics files in the filesystem, handling all filename formats."""
    lyrics_files = []
    potential_lyrics_files = []  # For debug logging
    logging.info(f"Searching for lyrics files in {base_dir}")
    
    try:
        # Search all files recursively
        for root, dirs, files in os.walk(base_dir):
            # Skip the tools directory to avoid self-referential files
            if "tools" in root.split(os.path.sep):
                continue
                
            for file in files:
                # Log potential lyrics files for debugging
                if "lyric" in file.lower() or "song" in file.lower() or "text" in file.lower():
                    potential_lyrics_files.append(os.path.join(root, file))
                
                # Fully case-insensitive matching for _lyrics.txt
                if file.lower().endswith('_lyrics.txt'):
                    # Skip the consolidated_songs_lyrics.txt file
                    if file.lower() == "consolidated_songs_lyrics.txt":
                        continue
                        
                    full_path = os.path.join(root, file)
                    if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                        lyrics_files.append(full_path)
                        logging.info(f"Found valid lyrics file (_lyrics.txt): {full_path}")
        
        # Log potential lyrics files that weren't included
        for file_path in potential_lyrics_files:
            if file_path not in lyrics_files:
                logging.debug(f"Potential lyrics file not matching pattern: {file_path}")
                
        logging.debug(f"All directories searched")
    except Exception as e:
        logging.error(f"Error searching directory {base_dir}: {str(e)}")
        raise
    
    logging.info(f"Found {len(lyrics_files)} valid lyrics files")
    return lyrics_files

def normalize_title(title):
    """
    Use directory name as-is with minimal normalization.
    Just normalize spacing to avoid leading/trailing whitespace issues.
    """
    # Only normalize spacing
    return ' '.join(title.split())

def read_lyrics_file(file_path):
    """Read the lyrics file and return its content."""
    try:
        # Validate file exists and is readable
        if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
            raise ValueError(f"File {file_path} is not accessible")
            
        # Read file content with proper encoding
        with open(file_path, "r", encoding='utf-8') as f:
            lyrics = f.read().strip()
        
        # Get the title from the directory name (as-is)
        dir_name = os.path.basename(os.path.dirname(file_path))
        # Only apply minimal normalization
        title = normalize_title(dir_name)
        
        logging.info(f"Processed {file_path} with title: {title}")
        
        return {
            "title": title,
            "lyrics": lyrics
        }
    except (ValueError, UnicodeDecodeError) as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading {file_path}: {str(e)}")
        raise

def str_presenter(dumper, data):
    """Force block scalar style for multiline strings."""
    if "\n" in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def consolidate_songs(base_dir: str = "..", output_file: str = "../consolidated_songs.yml", dry_run: bool = False):
    """Consolidate all lyrics files into a single YAML file."""
    lyrics_files = find_lyrics_files(base_dir)
    
    # Create backup of existing file if it exists and we're not in dry-run mode
    if os.path.exists(output_file) and not dry_run:
        backup_file = f"{output_file}.bak"
        if os.path.exists(backup_file):
            # If backup exists, remove it first
            os.remove(backup_file)
        shutil.copy2(output_file, backup_file)
        logging.info(f"Created backup: {backup_file}")
        print(f"Backup created: {backup_file}")
    
    # Initialize sets for tracking processed songs and versions
    processed_titles = set()
    duplicates = {}  # Store paths for each duplicate title
    
    # Process all files, including those in subdirectories
    # The consolidated_songs_lyrics.txt file is already filtered out in find_lyrics_files
    
    # Process files to get current songs
    current_songs = []
    for file in lyrics_files:
        try:
            logging.info(f"Processing file: {file}")
            
            # Read lyrics file and get title
            song_data = read_lyrics_file(file)
            
            # Check for duplicates
            if song_data["title"] in processed_titles:
                if song_data["title"] not in duplicates:
                    duplicates[song_data["title"]] = []
                duplicates[song_data["title"]].append(file)
                logging.info(f"Found duplicate: {song_data['title']} at {file}")
                continue
            
            processed_titles.add(song_data["title"])
            current_songs.append(song_data)
        except Exception as e:
            logging.error(f"Error processing {file}: {str(e)}")
            continue

    # Only regenerate if there are changes
    if not os.path.exists(output_file):
        songs = current_songs
        print(f"Creating {output_file} from {len(songs)} songs")
    else:
        # Load existing songs
        with open(output_file, "r", encoding='utf-8') as f:
            existing_data = yaml.safe_load(f)
            existing_songs = existing_data.get("songs", [])
            
        # Compare existing and current songs
        existing_titles = {song["title"] for song in existing_songs}
        current_titles = {song["title"] for song in current_songs}
        
        if existing_titles != current_titles:
            songs = current_songs
            print(f"Updating {output_file} with {len(songs)} songs")
        else:
            print(f"No changes detected in {output_file}")
            return

    if songs:
        try:
            # Sort songs alphabetically by title
            songs.sort(key=lambda x: x["title"])
            
            if not dry_run:
                with open(output_file, "w", encoding='utf-8') as f:
                    yaml.dump({"songs": songs}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Generate summary
            print("\nProcessing Summary:")
            print(f"Total files processed: {len(lyrics_files)}")
            print(f"Unique songs found: {len(songs)}")
            print(f"Duplicate songs skipped: {len(duplicates)}")
            if duplicates:
                print("\nFound duplicate titles (some may be intentional translations):")
                for title, paths in sorted(duplicates.items()):
                    print(f"- {title}:")
                    for path in paths:
                        print(f"  - {path}")
                print("\nNote: Some duplicates are intentional translations of the same song in different languages.")
            
            if not dry_run:
                logging.info(f"Successfully consolidated {len(songs)} songs into {output_file}")
                print(f"\nConsolidated {len(songs)} songs into {output_file}")
            else:
                print("\n(Dry run mode - no files were written)")
        except Exception as e:
            logging.error(f"Error writing to {output_file}: {str(e)}")
            raise
    else:
        logging.warning("No valid songs found to consolidate")
        print("No valid songs found to consolidate.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Consolidate lyrics files into a YAML file')
    parser.add_argument('--base-dir', default='.',
                        help='Base directory to search for lyrics files (default: current directory)')
    parser.add_argument('--output', default='consolidated_songs.yml',
                        help='Output YAML file path (default: consolidated_songs.yml)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without writing to output file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler('consolidate_songs.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Validate paths
        base_dir = os.path.abspath(args.base_dir)
        output_file = os.path.abspath(args.output)
        
        if not os.path.isdir(base_dir):
            raise ValueError(f"Base directory {base_dir} does not exist")
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        start_time = time.time()
        consolidate_songs(base_dir, output_file, args.dry_run)
        end_time = time.time()
        
        logging.info(f"Processing completed in {end_time - start_time:.2f} seconds")
        
    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
