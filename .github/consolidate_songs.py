import os
import yaml

def parse_first_yml(folder):
    """Parse the first .yml file found in the folder."""
    for file in os.listdir(folder):
        if file.endswith(".yml"):
            with open(os.path.join(folder, file), "r") as f:
                return yaml.safe_load(f)
    return None

def consolidate_songs():
    """Walk through folders and consolidate song data."""
    songs = {}
    for root, dirs, files in os.walk("."):
        if os.path.basename(root) == ".":
            continue  # Skip the root directory
        song_data = parse_first_yml(root)
        if song_data:
            folder_name = os.path.basename(root)
            songs[folder_name] = song_data

    with open("consolidated_songs.yml", "w") as f:
        yaml.dump({"songs": songs}, f, default_flow_style=False)

if __name__ == "__main__":
    consolidate_songs()
