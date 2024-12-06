import os
import yaml

def find_lyrics_files(base_dir):
    """Find all files matching the '_lyrics.txt' pattern."""
    lyrics_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith("_lyrics.txt"):
                lyrics_files.append(os.path.join(root, file))
    return lyrics_files

def read_lyrics_file(file_path):
    """Read the lyrics file and return its content."""
    with open(file_path, "r") as f:
        content = f.read()
    # Use the folder name as the song title
    title = os.path.basename(os.path.dirname(file_path)).replace("-", " ").title()
    return {"title": title, "lyrics": content.strip()}

def consolidate_songs(base_dir, output_file):
    """Consolidate all lyrics files into a single YAML file."""
    songs = []
    lyrics_files = find_lyrics_files(base_dir)
    
    for file in lyrics_files:
        song_data = read_lyrics_file(file)
        songs.append(song_data)

    # Write consolidated data to the output YAML file
    with open(output_file, "w") as f:
        yaml.dump({"songs": songs}, f, default_flow_style=False, allow_unicode=True)

if __name__ == "__main__":
    base_directory = "."
    output_file = "consolidated_songs.yml"
    consolidate_songs(base_directory, output_file)
    print(f"Consolidated {len(find_lyrics_files(base_directory))} songs into {output_file}")
