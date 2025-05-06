import os
import yaml
from yaml.representer import SafeRepresenter
import logging
from datetime import datetime
import time
from tqdm import tqdm
import shutil
import argparse
import sys
from pathlib import Path

def find_lyrics_files(base_dir):
    """Find all files matching the '_lyrics.txt' pattern."""
    lyrics_files = []
    logging.info(f"Searching for lyrics files in {base_dir}")
    
    try:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('_lyrics.txt'):
                    full_path = os.path.join(root, file)
                    # Validate file exists and is readable
                    if os.path.isfile(full_path) and os.access(full_path, os.R_OK):
                        lyrics_files.append(full_path)
                        logging.debug(f"Found lyrics file: {full_path}")
                    else:
                        logging.warning(f"Skipping invalid file: {full_path}")
    except Exception as e:
        logging.error(f"Error searching directory {base_dir}: {str(e)}")
        raise
    
    logging.info(f"Found {len(lyrics_files)} valid lyrics files")
    return lyrics_files

def normalize_title(title):
    """Normalize song titles to match the expected format."""
    # Handle known special cases
    special_cases = {
        "Carpe Diem -seize the day": "Carpe Diem   Seize The Day",
        "The Journey's the Destination": "The Journey'S The Destination",
        "The Tone of the Heart": "The Tone Of The Heart",
        "The Journey to Myself": "The Journey To Myself",
        "Youtubero Aventurero": "Youtuber Aventurero",
        "Faro y Reflejo": "Faro Y Reflejo",
        "¿Habrá Un Mañana?": "¿Habrá Un Mañana?",
        "Y Aura-t-il Demain?": "¿Habrá Un Mañana?",
        "Un Nuevo Amanezer": "Un Nuevo Amanezer",
        "You'll always be my spark": "You'Ll Always Be My Spark",
        "Una Foto Para Recordar": "Un Foto Para Recordar",
        "Sleepless In Dreamland 1": "Sleepless In Dreamland",
        "Slow Dancing In Time 1": "Slow Dancing In Time",
        "Under The Red Star. V2": "Under The Red Star"
    }
    
    # Normalize spacing
    normalized = title.replace("-", " ").replace("_", " ").strip()
    
    # Remove number suffixes first
    normalized = normalized.replace(" 1", "").replace(". V2", "")
    
    # Handle special characters
    # Use proper unicode normalization
    normalized = normalized.encode('utf-8').decode('utf-8')
    
    # Convert to title case
    normalized = normalized.title()
    
    # Apply special cases
    if normalized in special_cases:
        normalized = special_cases[normalized]
    
    # Remove any remaining numbers at the end if they're not part of a special case
    if normalized and normalized[-1].isdigit() and normalized not in special_cases.values():
        normalized = normalized[:-1].strip()
    
    return normalized

def read_lyrics_file(file_path):
    """Read the lyrics file and return its content."""
    try:
        # Validate file exists and is readable
        if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
            raise ValueError(f"File {file_path} is not accessible")
            
        # Read file content
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.read().splitlines()
        content = "\n".join(lines)
        
        # Get the title from the directory name
        dir_name = os.path.basename(os.path.dirname(file_path))
        title = normalize_title(dir_name)
        
        logging.info(f"Processed {file_path} with title: {title}")
        
        return {
            "title": title,
            "lyrics": content
        }
    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}")
        raise
    except UnicodeDecodeError:
        logging.error(f"Unicode error reading {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        raise
    except UnicodeDecodeError:
        logging.error(f"Unicode error reading {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        raise

def str_presenter(dumper, data):
    """Force block scalar style for multiline strings."""
    if "\n" in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def consolidate_songs(base_dir, output_file, dry_run=False):
    """Consolidate all lyrics files into a single YAML file."""
    lyrics_files = find_lyrics_files(base_dir)
    
    # Create backup of existing file if it exists and we're not in dry-run mode
    if os.path.exists(output_file) and not dry_run:
        backup_file = f"{output_file}.bak"
        shutil.copy2(output_file, backup_file)
        logging.info(f"Created backup: {backup_file}")
    
    # Skip the root directory file if it exists
    lyrics_files = [f for f in lyrics_files if not os.path.basename(f) == "consolidated_songs_lyrics.txt"]
    
    processed_titles = set()
    duplicates = set()
    
    # Process files to get current songs
    current_songs = []
    for file in lyrics_files:
        try:
            logging.info(f"Processing file: {file}")
            song_data = read_lyrics_file(file)
            title = song_data["title"]
            
            # Skip if we've already processed this title
            if title in processed_titles:
                duplicates.add(title)
                logging.info(f"Skipping duplicate: {title}")
                continue
                
            processed_titles.add(title)
            current_songs.append(song_data)
        except Exception as e:
            logging.error(f"Error processing {file}: {str(e)}")
            continue

    # Load existing songs if file exists
    existing_songs = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_songs = yaml.safe_load(f).get('songs', [])

    # Create final list of songs
    songs = []
    existing_titles = {song["title"] for song in existing_songs}
    
    # Add current songs
    for song in current_songs:
        title = song["title"]
        if title in processed_titles:
            duplicates.add(title)
            logging.info(f"Skipping duplicate: {title}")
        else:
            logging.info(f"Adding song: {title}")
            songs.append(song)
            processed_titles.add(title)
    
    # Remove songs that no longer exist
    for song in existing_songs:
        title = song["title"]
        if title in processed_titles:
            songs.append(song)

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
                print("\nDuplicate titles:")
                for title in sorted(duplicates):
                    print(f"- {title}")
            
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
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
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
