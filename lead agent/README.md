# Vela Strategies — Lead Generator Agent

Finds Portuguese news stories that might signal a small business needing
what Vela does (automation, dashboards, systems integration), using only
free sources: Google News (no key needed) and a local LLM via Ollama.

## How it works — three stages

1. **Researcher** — searches Google News for a list of keywords, gathers
   candidate articles. No judgement here, just evidence-gathering.
2. **Analyst** — reads each article and asks a local LLM to classify it as
   `prospect`, `competitor`, or `irrelevant`, with a score and a reason.
3. **Critic** — a *separate* LLM pass that checks whether the Analyst's
   reason is actually backed by the article text, or whether it's a
   confident guess. This is the step that catches hallucinated leads
   before they land in your spreadsheet.

Splitting these three apart (rather than one LLM call that both finds and
judges a lead) is deliberate — it's much harder for a bad guess to slip
through when a second, independent pass has to justify it against the
same evidence.

## One-time setup

```bash
pip install requests beautifulsoup4 lxml
```

Install [Ollama](https://ollama.com) if you don't have it, then pull a
model:

```bash
ollama pull qwen2.5:7b
```

Ollama usually starts running automatically after install. If a run of
the script says it can't reach Ollama, open a terminal and run:

```bash
ollama serve
```

## Running it

```bash
python lead_gen.py
```

Output goes to `leads.csv` in the same folder — open it in Excel/Numbers/
Google Sheets like any spreadsheet. Columns:

| column | meaning |
|---|---|
| classification | prospect / competitor / irrelevant |
| score | 0–100, after the Critic's adjustment |
| critic_verdict | confirmed / revised / rejected / skipped |
| reason | the Analyst's one-line reasoning |
| critic_notes | why the Critic confirmed, revised, or rejected it |
| title, source, url | the original article |

`seen_urls.txt` tracks every article already processed, so re-running the
script later (daily, weekly — whatever fits your 5–10 hours) only looks
at new articles. Safe to schedule or just run by hand whenever.

## Tuning it

All the knobs are at the top of `lead_gen.py`, under `CONFIG`:

- **`KEYWORDS`** — the actual search terms. This is the thing most worth
  iterating on. If you're not getting good results, this is usually why —
  try more specific or more varied phrasing.
- **`VELA_DESCRIPTION`** — what the LLM is told Vela does. Keep this in
  sync with however you're currently describing the business.
- **`CRITIC_ENABLED`** — turn off to skip the Critic pass entirely
  (faster, cheaper on your machine, but less protection against a
  confidently-wrong Analyst call).
- **`MIN_SCORE_FOR_CRITIC`** — obvious non-matches skip the Critic call
  entirely, to save time.

## Honest limitations

- Article text extraction is intentionally simple (grabs `<p>` tags) —
  it won't get everything cleanly off every site, especially ones with
  paywalls or heavy JavaScript. Good enough most of the time, not perfect.
- Google News RSS is unofficial and free — it can change behavior without
  warning. If searches suddenly return nothing, that's the first place
  to check.
- A local model like Qwen 7B is capable but not flawless. Treat
  `prospect` classifications as a shortlist to review, not a guarantee —
  the Critic pass reduces false positives, it doesn't eliminate them.
