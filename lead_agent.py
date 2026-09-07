
import os
import json
import requests


# ============================================================
# CONFIGURATION
# ============================================================

SEARCH_URL = "http://localhost:8080/search"
QWEN_URL = "http://localhost:11434/api/generate"
QWEN_MODEL = "qwen3:1.7b"


# ============================================================
# SCORING RUBRIC
# ============================================================

SCORE_WEIGHTS = {
    "portugal": 15,
    "porto_gaia": 10,
    "employees_5_100": 10,
    "hiring": 15,
    "website_modernization": 15,
    "digital_transformation": 10,
    "no_internal_tech_team": 10,
    "expansion_news": 10,
    "decision_maker": 5,
}


# ============================================================
# SEARCH
# ============================================================

search_response = requests.get(
    SEARCH_URL,
    params={
        "q": "Porto Portugal company expansion hiring new facility growth",
        "format": "json"
    },
    timeout=30
)

search_response.raise_for_status()

results = search_response.json()["results"][:10]


# ============================================================
# PROCESS EACH SEARCH RESULT
# ============================================================

for result in results:

    company_info = f"""
Title: {result.get("title", "")}
Description: {result.get("content", "")}
URL: {result.get("url", "")}
"""

    prompt = f"""
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

First identify the ACTUAL COMPANY being discussed.

Do not identify the search engine, publisher, website, or news organization
as the company.

Then classify the result as exactly one of:

- "prospect"
- "competitor"
- "irrelevant"

A prospect should be a real business that could reasonably purchase
Vela's services.

============================================================
SCORING SIGNALS
============================================================

Evaluate the search result against these EXACT signals.

1. portugal
   +15 points

   Is there evidence that the actual company operates, is expanding,
   investing, hiring, or doing business in Portugal?

2. porto_gaia
   +10 points

   Is there evidence specifically connecting the company to Porto,
   Vila Nova de Gaia, or the surrounding Porto/Gaia area?

3. employees_5_100
   +10 points

   Is there evidence that the company has approximately 5–100 employees?

   Only mark this true when the result provides evidence for the
   employee range. Do not guess based on company size.

4. hiring
   +15 points

   Is there evidence that the company is currently hiring or has
   recent hiring activity?

5. website_modernization
   +15 points

   Is there actual evidence that the company's website appears outdated,
   poorly maintained, difficult to use, technically weak, or otherwise
   presents a possible website modernization opportunity?

   Do NOT assume a website needs modernization merely because it is old.

6. digital_transformation
   +10 points

   Is there actual evidence of digital transformation, automation,
   technology modernization, systems integration, software/process
   improvement, or a similar technology initiative?

   Do NOT assume that a company needs digital transformation simply
   because it is growing.

7. no_internal_tech_team
   +10 points

   Is there evidence that the company does NOT appear to have an obvious
   internal technology/IT team?

   Only mark this true when there is reasonable evidence.

   Lack of evidence about an IT team is NOT automatically proof that
   there is no internal technology team.

8. expansion_news
   +10 points

   Is there evidence of recent expansion, a new facility, investment,
   acquisition, geographic expansion, growth, or other significant
   business development?

9. decision_maker
   +5 points

   Is an identifiable decision-maker or relevant person mentioned,
   such as a founder, CEO, CTO, COO, operations manager, IT manager,
   or other person who could potentially influence purchasing?

============================================================
IMPORTANT EVIDENCE RULE
============================================================

This is the MOST IMPORTANT rule in the task.

You are evaluating the SEARCH RESULT, not guessing what might be true
about the company.

A signal may ONLY be marked true when the provided search result contains
direct evidence supporting that specific signal.

If the result does not provide evidence for a signal, mark it false.

NEVER turn an assumption, implication, possibility, or industry stereotype
into evidence.

Examples:

- A new factory is evidence of expansion_news.
  A new factory is NOT automatically evidence of digital_transformation.

- A company being a technology company is NOT evidence that it has
  digital_transformation needs.

- A company being in Porto is evidence for porto_gaia.
  A company being in Lisbon is NOT evidence for porto_gaia.

- Not seeing an IT department mentioned is NOT evidence of
  no_internal_tech_team.

- A company having 200 employees is NOT evidence for employees_5_100.

- A company hiring is evidence for hiring.
  Hiring is NOT automatically evidence of digital_transformation.

- A company operating in aerospace, manufacturing, logistics,
  hospitality, technology, or another industry does NOT make it a
  competitor.

- A company is a competitor ONLY when its primary business is providing
  technology consulting, software development, automation, AI,
  IT outsourcing, or similar technology services to other businesses.

- A company being large, successful, or growing does NOT automatically
  mean it needs Vela's services.

When evidence is ambiguous, choose FALSE.

When evidence is missing, choose FALSE.

When evidence supports only one signal, mark only that signal true.

Do not use knowledge from outside the provided search result.

For every signal marked TRUE, provide the exact fact from the search
result that supports it.

For signals marked FALSE, leave the evidence field empty.

Your job is to identify evidence, NOT to make optimistic sales assumptions.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use this exact structure:

{{
    "company": "actual company name",
    "type": "prospect",
    "signals": {{
        "portugal": {{
            "supported": false,
            "evidence": ""
        }},
        "porto_gaia": {{
            "supported": false,
            "evidence": ""
        }},
        "employees_5_100": {{
            "supported": false,
            "evidence": ""
        }},
        "hiring": {{
            "supported": false,
            "evidence": ""
        }},
        "website_modernization": {{
            "supported": false,
            "evidence": ""
        }},
        "digital_transformation": {{
            "supported": false,
            "evidence": ""
        }},
        "no_internal_tech_team": {{
            "supported": false,
            "evidence": ""
        }},
        "expansion_news": {{
            "supported": false,
            "evidence": ""
        }},
        "decision_maker": {{
            "supported": false,
            "evidence": ""
        }}
    }},
    "reason": "short explanation of the overall classification"
}}

Remember:

DO NOT calculate or provide a score.

Python will calculate the score from the signals.
"""


    # ========================================================
    # ASK QWEN TO ANALYZE THE RESULT
    # ========================================================

    response = requests.post(
        QWEN_URL,
        json={
            "model": QWEN_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    answer = response.json()["response"]


    # ========================================================
    # PARSE QWEN'S JSON
    # ========================================================

    try:
        analysis = json.loads(answer)

    except json.JSONDecodeError:

        print("\nQwen returned invalid JSON:")
        print(answer)
        print("-" * 60)

        continue


    # ========================================================
    # CALCULATE SCORE
    # ========================================================

    score = 0

    signals = analysis.get("signals", {})

    for signal, points in SCORE_WEIGHTS.items():

        signal_data = signals.get(signal, {})

        if signal_data.get("supported") is True:
            score += points


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print("\n" + "=" * 60)

    print(f"Company: {analysis.get('company', 'Unknown')}")
    print(f"Type: {analysis.get('type', 'Unknown')}")
    print(f"Score: {score}/100")

    print("\nSignals:")

    for signal, points in SCORE_WEIGHTS.items():

        signal_data = signals.get(signal, {})

        supported = signal_data.get("supported", False)
        evidence = signal_data.get("evidence", "")

        if supported:
            print(f"  [+{points}] {signal}")
            print(f"       Evidence: {evidence}")

        else:
            print(f"  [ 0] {signal}")

    print("\nReason:")
    print(analysis.get("reason", ""))

    print("\nSource:")
    print(result.get("url", ""))

    print("=" * 60)

