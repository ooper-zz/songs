import yaml

with open('song_tags.yml', 'r') as f:
    data = yaml.safe_load(f)

missing = []
for title, song in data['songs'].items():
    if 'tags' not in song:
        missing.append((title, 'tags'))
    if 'notes' not in song:
        missing.append((title, 'notes'))

print('Missing fields:', missing)
