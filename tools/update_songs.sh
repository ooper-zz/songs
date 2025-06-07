#!/bin/bash

# Get the full path to the script directory
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Starting update at $(date)"
echo "Script directory: $SCRIPT_DIR"

echo "Running consolidate_songs.py..."
python3 "$SCRIPT_DIR/consolidate_songs.py" --base-dir "$SCRIPT_DIR/.." --output "$SCRIPT_DIR/consolidated_songs.yml"
echo "consolidate_songs.py exit code: $?"

echo "Running generate_song_metadata.py..."
python3 "$SCRIPT_DIR/generate_song_metadata.py" --output "$SCRIPT_DIR/song_metadata.yml"
echo "generate_song_metadata.py exit code: $?"

echo "Update completed at $(date)"
