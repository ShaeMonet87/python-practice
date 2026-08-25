import json
from collections import Counter

with open("discogs_collection.json", "r") as file:
    all_records = json.load(file)

print(f"Total records: {len(all_records)}")

# Genres
genres = Counter()

for item in all_records:
    basic = item["basic_information"]

    for genre in basic.get("genres", []):
        genres[genre] += 1

print("\nTop genres:")

for genre, count in genres.most_common():
    print(f"{genre}: {count}")

# Artists
artists = Counter()

for item in all_records:
    basic = item["basic_information"]

    for artist in basic.get("artists", []):
        artists[artist["name"]] += 1

print("\nTop artists:")

for artist, count in artists.most_common(20):
    print(f"{artist}: {count}")

# Decades
years = Counter()

for item in all_records:
    year = item["basic_information"].get("year")

    if year:
        years[year // 10 * 10] += 1

print("\nRecords by decade:")

for decade, count in sorted(years.items()):
    print(f"{decade}s: {count}")
