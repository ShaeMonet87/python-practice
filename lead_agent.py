import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

companies = [
    {
        "name": "Atlantic Logistics",
        "industry": "Logistics",
        "employees": 85,
        "growing": True,
        "hiring_tech": False,
        "new_location": True,
        "needs_automation": True
    },
    {
        "name": "Porto Design Studio",
        "industry": "Design",
        "employees": 12,
        "growing": False,
        "hiring_tech": False,
        "new_location": False,
        "needs_automation": False
    },
    {
        "name": "Lusitania Health",
        "industry": "Healthcare",
        "employees": 140,
        "growing": True,
        "hiring_tech": True,
        "new_location": True,
        "needs_automation": True
    }
]
for company in companies:
    score = 0
    reasons = []
    if company["growing"]:
        score += 20
        reasons.append("company is growing")

    if company["hiring_tech"]:
        score += 30
        reasons.append("hiring technology workers")

    if company["new_location"]:
        score += 20
        reasons.append("opening a new location")

    if company["needs_automation"]:
        score += 30
        reasons.append("may need automation")

    if score >= 80:
        rating = "High"
    elif score >= 50:
        rating = "Medium"
    else:
        rating = "Low"

    print(company["name"], score)
    print("Rating:", rating)
    print("Reasons:", reasons)
    print()

company_description = """
Atlantic Logistics is expanding into northern Spain.
The company is increasing its warehouse operations
and looking for ways to automate its logistics processes.
"""

print(company_description)

chat = client.chats.create(
    model="gemini-3.6-flash"
)

response = chat.send_message(
    f"""
Analyze this company as a potential lead for an IT consulting business.

Company information:
{company_description}

Determine these four signals:

- growing
- hiring_tech
- new_location
- needs_automation

Return ONLY valid JSON in this exact format:

{{
    "growing": true,
    "hiring_tech": false,
    "new_location": true,
    "needs_automation": true
}}
"""
)

signals = json.loads(response.text)

gemini_score = 0

if signals["growing"]:
    gemini_score += 20

if signals["hiring_tech"]:
    gemini_score += 30

if signals["new_location"]:
    gemini_score += 20

if signals["needs_automation"]:
    gemini_score += 30

print("Final Gemini-based score:", gemini_score)

if gemini_score >= 80:
    gemini_rating = "High"
elif gemini_score >= 40:
    gemini_rating = "Medium"
else:
    gemini_rating = "Low"

print("Gemini lead rating:", gemini_rating)