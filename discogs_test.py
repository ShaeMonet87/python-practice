import json
from collections import Counter

with open("discogs_collection.json", "r", encoding="utf-8") as file:
    data = json.load(file)

artists = Counter()

for item in data:
    basic = item["basic_information"]

    for artist in basic.get("artists", []):
        artists[artist["name"]] += 1

print("\nTop 30 artists in your collection:\n")

for artist, count in artists.most_common(30):
    print(f"{artist}: {count}")
    
