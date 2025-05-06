# Songs Repository

This repository contains song lyrics and metadata organized in a structured format.

## Structure

- Each song is stored in its own folder
- Lyrics are stored in `song_name_lyrics.txt` files
- Two main YAML files maintain metadata:
  - `consolidated_songs.yml`: Main consolidated metadata
  - `song_tags.yml`: Tag-based organization

## Tools

### Watcher Script
- Monitors folder changes
- Triggers updates to both YAML files
- Located in `watch_songs.py`

### Consolidation Scripts
- `consolidate_songs.py`: Updates `consolidated_songs.yml`
- `generate_song_tags.py`: Updates `song_tags.yml`

## Usage

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install watchdog pyyaml
   ```
4. Start the watcher:
   ```bash
   python watch_songs.py start
   ```

5. Stop the watcher:
   ```bash
   python watch_songs.py stop
   ```

## Development

To make changes:
1. Modify song folders
2. The watcher will automatically update both YAML files
3. Changes will be reflected in both `consolidated_songs.yml` and `song_tags.yml`
