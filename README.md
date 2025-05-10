# Song Management System

This repository contains scripts for managing and consolidating song lyrics and metadata.

## Installation Requirements

To use all features of the system, including diagram visualization, you'll need to install the following dependencies:

1. **Java** (required for PlantUML):
   ```bash
   brew install openjdk
   ```

2. **Graphviz** (for diagram rendering):
   ```bash
   brew install graphviz
   ```

3. **PlantUML** (for diagram visualization):
   ```bash
   brew install plantuml
   ```

After installation, the system diagrams in the README will be properly rendered.

## Purpose

The system helps maintain a centralized database of song lyrics and their associated metadata (tags, notes, etc.) by:
1. Automatically consolidating lyrics from multiple files
2. Maintaining consistent metadata across different versions of songs
3. Supporting multiple language versions of the same song
4. Automatically updating files when changes are detected

## Purpose

The system helps maintain a centralized database of song lyrics and their associated metadata (tags, notes, etc.) by:
1. Automatically consolidating lyrics from multiple files
2. Maintaining consistent metadata across different versions of songs
3. Supporting multiple language versions of the same song
4. Automatically updating files when changes are detected

## Workflow

```plantuml
@startuml

skinparam defaultFontSize 12
skinparam defaultFontName Arial
skinparam shadowing false

start

:Start;

repeat
    :Add New Song?;

### 1. Adding a New Song

1. **Create Song Folder**
   - Create a new folder with the song title
   - The folder name will be automatically normalized to lowercase with hyphens
   - Example: `Madre y Padre a la Vez` becomes `madre-y-padre-a-la-vez`

2. **Add Lyrics File**
   - Create a lyrics file in the format: `<song-name>_lyrics.txt`
   - The first line of the file should be the actual song title
   - Example: `madre-y-padre-a-la-vez_lyrics.txt`

3. **Normalize Folder Name**
   ```bash
   python tools/normalize_song_metadata.py "Madre y Padre a la Vez"
   ```
   - This script will:
     - Normalize the folder name
     - Update `song_metadata.yml` with the actual title
     - Ensure consistent naming

4. **Add Metadata**
   ```bash
   python tools/manage_song_metadata.py
   ```
   - Use the interactive menu to:
     - Add new song
     - Enter metadata (tags, status, notes)

### 2. Updating an Existing Song

1. **Update Lyrics**
   - Edit the lyrics file directly
   - Changes will be automatically detected

2. **Update Metadata**
   ```bash
   python tools/manage_song_metadata.py
   ```
   - Use the interactive menu to:
     - Select the song to update
     - Modify metadata fields
     - Add/remove tags
     - Add/remove notes
     - Change status

3. **Rename Song**
   - If needed, use the management script to rename:
   ```bash
   python tools/manage_song_metadata.py
   ```
   - Select "Rename song" from the menu
   - Follow the prompts to rename the song
   - The script will handle folder renaming and metadata updates

### 3. Managing Multiple Versions

1. **Add New Version**
   - Create a new folder for the version
   - Use the management script to link versions
   - Add version-specific metadata

2. **Consolidate Lyrics**
   ```bash
   python tools/consolidate_songs.py
   ```
   - This script will:
     - Consolidate all lyrics files
     - Update `consolidated_songs.yml`
     - Maintain version history

### 4. Best Practices

1. **Naming Conventions**
   - Use descriptive song titles
   - Include language indicators for non-English songs
   - Use consistent formatting for song versions

2. **Metadata Management**
   - Update metadata immediately after changes
   - Use descriptive tags
   - Document important notes
   - Maintain accurate status

3. **Version Control**
   - Commit changes after each major update
   - Include descriptive commit messages
   - Push changes to remote repository

## Folder Naming Convention

To ensure consistency and compatibility across different systems, song folders follow a specific naming convention:

1. **Format**: All folder names are in lowercase with hyphens separating words (kebab-case)
   - Example: `madre-y-padre-a-la-vez`
   - Special characters are removed or replaced with appropriate text

2. **Actual Song Titles**:
   - The actual song titles (with proper capitalization and special characters) are stored in the `song_tags.yml` file under the `actual_title` key
   - This allows for proper display of titles while maintaining a consistent folder structure

3. **Language Support**:
   - The system supports multiple languages while maintaining a consistent folder structure
   - Special characters from different languages (e.g., French accents, Spanish question marks) are preserved in the actual titles but normalized in folder names

4. **Benefits**:
   - Git-friendly folder names that work across different operating systems
   - Consistent structure for automation and scripting
   - Preserved actual song titles for display and content generation
   - Easy to read and maintain folder structure

5. **Examples**:
   - Original: `Aura-t-il Demain ?`
   - Normalized: `aura-t-il-demain`
   - Actual title in `song_metadata.yml`: `Aura-t-il Demain ?`

   - Original: `¿Habrá un Mañana?`
   - Normalized: `habra-un-mañana`
   - Actual title in `song_metadata.yml`: `¿Habrá un Mañana?`

## Scripts

All scripts are located in the `tools/` directory.

### 1. `tools/normalize_new_song.py`

Purpose: Normalize new song folder names to maintain consistency

Usage:
```bash
python normalize_new_song.py <song_directory>
```

Example:
```bash
python normalize_new_song.py "My New Song"
```

This script will:
1. Normalize the folder name to lowercase with hyphens
2. Update `song_metadata.yml` with the actual song title
3. Ensure consistent naming across all songs

### 2. `tools/normalize_song_metadata.py`

Purpose: Normalize song keys in `song_metadata.yml` to match the folder naming convention

Usage:
```bash
python normalize_song_metadata.py
```

This script will:
1. Normalize all song keys in `song_metadata.yml` to lowercase with hyphens
2. Preserve actual song titles in the `actual_title` field
3. Ensure consistency between folder names and song keys

### Song Metadata Management Menu

The metadata management system provides an interactive menu for managing song metadata:

```
Song Metadata Management Menu:
1. List all songs
2. Add new song
3. Update song metadata
4. Delete song
5. Rename song
6. Exit
```

To use the menu, run:
```bash
python tools/manage_song_metadata.py
```

Each option allows you to:
1. List all songs - View all songs with their metadata
2. Add new song - Create a new song entry
3. Update song metadata - Modify existing metadata (tags, status, notes)
4. Delete song - Remove a song from the metadata
5. Rename song - Change a song's normalized name
6. Exit - Quit the menu

Tips:
- Use Tab to autocomplete song titles when selecting a song
- You can type part of a song title or use the number to select
- Press Ctrl+C at any time to exit gracefully

### 3. `tools/consolidate_songs.py`

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

### 2. `tools/generate_song_metadata.py`

Purpose: Generates and maintains song metadata.

Usage:
```bash
python tools/generate_song_metadata.py --base-dir .. --output ../song_metadata.yml
```

Options:
- `--base-dir`: Directory containing the lyrics files (default: parent directory)
- `--output`: Output YAML file path (default: parent directory/song_metadata.yml)

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
