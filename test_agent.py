import requests

# 1. Search SearXNG
search_response = requests.get(
    "http://localhost:8080/search",
    params={
        "q": "Porto software companies",
        "format": "json"
    }
)

results = search_response.json()["results"][:5]

# 2. Give the search results to Qwen
company_text = ""

for result in results:
    company_text += f"""
Company: {result["title"]}
Description: {result["content"]}
URL: {result["url"]}
"""

prompt = f"""
You are a sales lead analyst.

Review these companies found through a live web search:

{company_text}

For each company:
1. Give a lead score from 0-100.
2. Say whether it looks like a potential lead.
3. Give one short reason.

Keep your answer concise.
"""

# 3. Ask Qwen to analyze them
ai_response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:1.7b",
        "prompt": prompt,
        "stream": False
    }
)

print(ai_response.json()["response"])