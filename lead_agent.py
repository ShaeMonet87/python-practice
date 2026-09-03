import os
import json
import requests

search_response = requests.get(
    "http://localhost:8080/search",
    params={
        "q": "Porto Portugal company expansion hiring new facility growth",
        "format": "json"
    }
)

results = search_response.json()["results"][:10]

for result in results:

    company_info = f"""
Title: {result["title"]}
Description: {result["content"]}
URL: {result["url"]}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:1.7b",
            "prompt": f"""
You are qualifying sales leads for Vela Strategies.

Vela Strategies helps businesses improve their internal operations through:
- automation
- process improvement
- digital transformation
- technology modernization
- systems integration

IMPORTANT:
Vela is looking for BUSINESSES THAT COULD BUY THESE SERVICES.

A COMPETITOR is a company whose own business is primarily providing
technology consulting, software development, automation, AI, IT
outsourcing, or similar technology services to other businesses.

A company is NOT a competitor simply because it operates in technology,
manufacturing, aerospace, retail, logistics, finance, hospitality, or
another industry.

A company in those industries can still be a PROSPECT if it could
reasonably purchase Vela's services.

Also reject:
- job boards
- recruiting companies
- directories
- news organizations
- government/investment organizations
- generic articles that do not identify a potential customer

Analyze this search result:

{company_info}

Identify the ACTUAL COMPANY being discussed, not the website or publisher
that published the article.

Then classify the result as exactly one of:

- "prospect"
- "competitor"
- "irrelevant"

A prospect should be a real business that could reasonably need Vela's
services because of growth, expansion, operational complexity,
automation opportunities, or technology modernization.

Give the prospect a score from 0 to 100.

Return ONLY valid JSON in this exact format:

Return ONLY valid JSON in this exact format:

{{
    "company": "actual company name",
    "type": "prospect",
    "score": 0,
    "reason": "short explanation"
}}

""",
            "stream": False
        }
    )

    answer = response.json()["response"]

    print("\nQwen analysis:")
    print(answer)

