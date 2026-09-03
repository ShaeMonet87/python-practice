import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:1.7b",
        "prompt": "In one sentence, explain what a sales lead is.",
        "stream": False
    }
)

print(response.json()["response"])