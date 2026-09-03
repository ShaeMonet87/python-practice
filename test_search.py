import requests

url = "http://localhost:8080/search"

params = {
    "q": "Porto software companies",
    "format": "json"
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

data = response.json()

for result in data["results"][:5]:
    print("\nCompany:", result["title"])
    print("Description:", result["content"])
    print("URL:", result["url"])