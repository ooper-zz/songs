#!/usr/bin/env python3
import subprocess
import sys

def test_metadata_management():
    """Test the metadata management script."""
    # Add new song
    add_song = subprocess.Popen(
        ["python3", "tools/manage_song_metadata.py"],
        stdin=subprocess.PIPE,
        text=True
    )
    
    # Menu choice (Add new song)
    add_song.stdin.write("2\n")
    # Song title
    add_song.stdin.write("Test Song\n")
    # Confirm key
    add_song.stdin.write("y\n")
    # Enter metadata
    add_song.stdin.write("\n")  # Actual title
    add_song.stdin.write("y\n")  # Add tag
    add_song.stdin.write("test\n")  # Tag name
    add_song.stdin.write("n\n")  # No more tags
    add_song.stdin.write("deferred\n")  # Status
    add_song.stdin.write("y\n")  # Add note
    add_song.stdin.write("Test note\n")  # Note
    add_song.stdin.write("n\n")  # No more notes
    add_song.stdin.write("y\n")  # Confirm changes
    add_song.stdin.close()
    add_song.wait()
    
    # List songs
    list_songs = subprocess.Popen(
        ["python3", "tools/manage_song_metadata.py"],
        stdin=subprocess.PIPE,
        text=True
    )
    list_songs.stdin.write("1\n")
    list_songs.stdin.write("6\n")  # Exit
    list_songs.stdin.close()
    list_songs.wait()

if __name__ == "__main__":
    test_metadata_management()
