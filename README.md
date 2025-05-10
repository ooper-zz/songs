# Song Management System

This repository contains scripts for managing and consolidating song lyrics and metadata.

## Purpose

The system helps maintain a centralized database of song lyrics and their associated metadata (tags, notes, etc.) by:
1. Automatically consolidating lyrics from multiple files
2. Maintaining consistent metadata across different versions of songs
3. Supporting multiple language versions of the same song
4. Automatically updating files when changes are detected

## Scripts

All scripts are located in the `tools/` directory.

### 1. `tools/consolidate_songs.py`

Purpose: Consolidates all lyrics files into a single YAML file.

Usage:
```bash
python tools/consolidate_songs.py --base-dir .. --output ../consolidated_songs.yml
```

Options:
- `--base-dir`: Directory containing the lyrics files (default: parent directory)
- `--output`: Output YAML file path (default: parent directory/consolidated_songs.yml)
- `--dry-run`: Preview changes without writing to output file
- `--verbose`: Enable verbose logging

### 2. `tools/generate_song_tags.py`

Purpose: Generates and maintains metadata tags for each song.

Usage:
```bash
python tools/generate_song_tags.py --base-dir .. --output ../song_tags.yml
```

Options:
- `--base-dir`: Directory containing the lyrics files (default: parent directory)
- `--output`: Output YAML file path (default: parent directory/song_tags.yml)

### 3. `tools/watch_songs.py`

Purpose: Watches the directory for changes and automatically runs consolidation and tag generation.

Usage:
```bash
# Start the watcher
python tools/watch_songs.py start

# Stop the watcher
python tools/watch_songs.py stop
```

## Workflow

1. **Initial Setup**
   - Run `consolidate_songs.py` to create the initial consolidated file
   - Run `generate_song_tags.py` to create the initial tags file

2. **Ongoing Maintenance**
   - The watcher (`watch_songs.py`) will automatically:
     - Detect changes in song files
     - Run consolidation when lyrics change
     - Update tags when metadata changes

3. **Manual Updates**
   - Add new songs by creating `_lyrics.txt` files in appropriate directories
   - Add metadata by editing the `song_tags.yml` file
   - The watcher will automatically process these changes

## File Structure

- `_lyrics.txt`: Individual song lyrics files
- `consolidated_songs.yml`: Consolidated database of all songs and their lyrics
- `song_tags.yml`: Metadata and tags for each song
- `watch_songs.py`: Script for automatic monitoring and updates
- `consolidate_songs.py`: Script for manual consolidation
- `generate_song_tags.py`: Script for manual tag generation

## Notes

- The system supports multiple language versions of the same song
- Tags and notes are stored as lists in the YAML files
- The watcher creates backup files before making changes
- Logs are created for both consolidation and tag generation processes
