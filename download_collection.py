import os
import json
import requests

token = os.getenv("DISCOGS_TOKEN")

headers = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "DiscogsTestApp/1.0"
}

url = "https://api.discogs.com/users/shaemonet/collection/folders/0/releases"

all_records = []
page = 1

while True:
    params = {
        "page": page,
        "per_page": 50
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    all_records.extend(data["releases"])

    pages = data["pagination"]["pages"]

    print(f"Downloaded page {page} of {pages}")

    if page >= pages:
        break

    page += 1

with open("discogs_collection.json", "w") as file:
    json.dump(all_records, file, indent=2)

print(f"\nSaved {len(all_records)} records to discogs_collection.json")