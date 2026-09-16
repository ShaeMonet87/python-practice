"""
Vela Strategies — Lead Generator Agent
========================================

What this does, in plain terms:

  1. RESEARCHER  — searches Google News (free, no API key) for Portuguese
                    news stories that might signal a small business or
                    firm needing technical consulting (automation,
                    dashboards, workflow help).
  2. ANALYST     — for each result found, pulls the article text and asks
                    a local LLM (running on your machine via Ollama) to
                    decide: is this a PROSPECT, a COMPETITOR, or
                    IRRELEVANT — with a score and a one-line reason.
  3. CRITIC       — a second, separate LLM pass that checks the Analyst's
                    call against the actual evidence, so a lead doesn't
                    get saved just because the Analyst guessed confidently.
                    This is the step that catches hallucinated leads.

Everything runs locally and for free: no paid search API, no paid LLM API.
The only "cost" is your own electricity and time.

--------------------------------------------------------------------------
SETUP (one-time)
--------------------------------------------------------------------------
1. Install Python packages:
       pip install requests beautifulsoup4 lxml

2. Install Ollama (https://ollama.com) if you haven't already, then pull
   a model. Qwen is a good, capable, free choice:
       ollama pull qwen2.5:7b

3. Make sure Ollama is running (it usually runs automatically after
   install; if not, run `ollama serve` in a terminal).

4. Edit the CONFIG section below — at minimum, review KEYWORDS so the
   search terms match what a prospect for Vela actually looks like.

--------------------------------------------------------------------------
RUNNING IT
--------------------------------------------------------------------------
    python lead_gen.py

Each run:
  - Searches all KEYWORDS
  - Skips any article URL it has already seen (tracked in seen_urls.txt)
  - Appends new leads to leads.csv
  - Prints a short summary to the terminal

Re-running later only processes new articles — safe to run daily/weekly.
--------------------------------------------------------------------------
"""

import csv
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import quote

import requests

# ==========================================================================
# CONFIG — edit this section to fit Vela
# ==========================================================================

# Search terms fed to Google News. Keep these broad-but-relevant since
# Vela's positioning is general technical consulting, not one industry.
# Add / remove freely — one query per line.
KEYWORDS = [
    "PME Portugal contratação administrativo",
    "empresa Portugal processos manuais",
    "pequena empresa Portugal digitalização",
    "escritório Portugal expansão contratação",
    "startup Portugal automação processos",
]

# How Vela describes itself, used inside the LLM prompt so the model
# knows what counts as a "fit".
VELA_DESCRIPTION = (
    "Vela Strategies e uma consultoria tecnica em Portugal para pequenas "
    "equipas: automacao de processos, dashboards, e integracao de "
    "sistemas. Trabalha com qualquer pequena empresa ou escritorio que "
    "ainda faca trabalho repetitivo a mao (dados, ficheiros, relatorios) "
    "e nao tenha departamento de TI proprio."
)

# Ollama connection. Default is correct for a local install.
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:1.7b"   # change to whatever model you've pulled

# Set to False to skip the Critic pass entirely (faster, but less safe
# against hallucinated leads — Analyst's call goes straight to the CSV).
CRITIC_ENABLED = True

# Only articles scored at or above this by the Analyst get sent to the
# Critic at all (saves LLM calls on obvious non-matches).
MIN_SCORE_FOR_CRITIC = 40

# Files this script reads/writes, all in the same folder as this script.
OUTPUT_CSV = "leads.csv"
SEEN_URLS_FILE = "seen_urls.txt"

# How many articles to pull per keyword search (Google News RSS returns
# up to ~100, but you don't need that many per query).
RESULTS_PER_KEYWORD = 8

# Politeness delay between web requests, in seconds.
REQUEST_DELAY = 1.5


class _ParagraphTextParser(HTMLParser):
    """Extract readable text from paragraph elements without extra packages."""

    def __init__(self) -> None:
        super().__init__()
        self._in_paragraph = False
        self._current: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "p" and not self._in_paragraph:
            self._in_paragraph = True
            self._current = []

    def handle_data(self, data: str) -> None:
        if self._in_paragraph:
            self._current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "p" and self._in_paragraph:
            text = re.sub(r"\s+", " ", " ".join(self._current)).strip()
            if text:
                self.paragraphs.append(text)
            self._in_paragraph = False
            self._current = []


# ==========================================================================
# Data shape for one lead as it moves through the pipeline
# ==========================================================================

@dataclass
class Lead:
    title: str
    url: str
    source: str
    published: str
    evidence: str = ""          # extracted article text (trimmed)
    classification: str = ""    # "prospect" / "competitor" / "irrelevant"
    score: int = 0
    reason: str = ""
    critic_verdict: str = ""    # "confirmed" / "revised" / "rejected" / ""
    critic_notes: str = ""


# ==========================================================================
# STAGE 1 — RESEARCHER: find candidate articles
# ==========================================================================

def research_candidates(keywords: list[str]) -> list[Lead]:
    """Search Google News RSS for each keyword and return raw candidates.
    No judgement happens here — this stage only gathers evidence."""
    leads: list[Lead] = []
    seen_in_this_run = set()

    for kw in keywords:
        print(f"[researcher] searching: {kw}")
        query = quote(kw)
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=pt-PT&gl=PT&ceid=PT:pt"

        try:
            resp = requests.get(rss_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ! search failed for '{kw}': {e}")
            continue

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError as e:
            print(f"  ! could not parse RSS for '{kw}': {e}")
            continue

        items = root.findall("./channel/item")[:RESULTS_PER_KEYWORD]
        for item in items:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            source_el = item.find("source")
            source = source_el.text.strip() if source_el is not None and source_el.text else ""

            if not link or link in seen_in_this_run:
                continue
            seen_in_this_run.add(link)

            leads.append(Lead(title=title, url=link, source=source, published=pub_date))

        time.sleep(REQUEST_DELAY)

    print(f"[researcher] found {len(leads)} candidate articles total")
    return leads


def fetch_article_text(url: str, max_chars: int = 2000) -> str:
    """Best-effort extraction of readable text from an article page.
    This is intentionally simple (grab <p> tags) rather than using a
    heavier readability library — good enough to give the LLM real
    evidence without adding another dependency to install."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    parser = _ParagraphTextParser()
    try:
        parser.feed(resp.text)
        parser.close()
    except HTMLParser:
        return ""
    paragraphs = parser.paragraphs
    text = " ".join(paragraphs)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


# ==========================================================================
# STAGE 2 — ANALYST: classify each lead using the local LLM
# ==========================================================================

def call_ollama(prompt: str) -> str:
    """Send a prompt to the local Ollama server and return the raw text
    response. Raises on connection failure so callers can decide how to
    handle it (Ollama not running is the most common issue)."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "")


def parse_json_loosely(raw: str) -> dict:
    """LLMs sometimes wrap JSON in markdown fences or add stray text.
    Pull out the first {...} block and parse that."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def analyze_lead(lead: Lead) -> Lead:
    """Ask the LLM: prospect, competitor, or irrelevant — with a score
    and a short reason grounded in the evidence text."""
    prompt = f"""Es um assistente que avalia se uma noticia e sinal de uma
potencial oportunidade de negocio para a seguinte empresa:

{VELA_DESCRIPTION}

Noticia:
Titulo: {lead.title}
Fonte: {lead.source}
Texto: {lead.evidence if lead.evidence else "(sem texto disponivel, usa apenas o titulo)"}

Classifica esta noticia numa destas tres categorias:
- "prospect": sugere uma empresa/organizacao que poderia precisar dos
  servicos da Vela Strategies (sinais: crescimento, contratacao
  administrativa, processos manuais, queixas de ineficiencia, expansao).
- "competitor": e sobre outra empresa de consultoria/automacao/tecnologia
  que oferece servicos semelhantes.
- "irrelevant": nao tem relacao clara com nenhuma das anteriores.

Responde APENAS em JSON, neste formato exato:
{{"classification": "prospect|competitor|irrelevant", "score": 0-100, "reason": "uma frase curta em portugues explicando porque, baseada no texto"}}

Se o texto nao contiver evidencia suficiente para justificar a
classificacao, usa "irrelevant" e um score baixo em vez de adivinhar."""

    try:
        raw = call_ollama(prompt)
    except requests.RequestException as e:
        lead.classification = "irrelevant"
        lead.score = 0
        lead.reason = f"[erro ao contactar Ollama: {e}]"
        return lead

    data = parse_json_loosely(raw)
    lead.classification = data.get("classification", "irrelevant")
    try:
        lead.score = int(data.get("score", 0))
    except (TypeError, ValueError):
        lead.score = 0
    lead.reason = data.get("reason", "").strip()
    return lead


# ==========================================================================
# STAGE 3 — CRITIC: double-check the Analyst's call against the evidence
# ==========================================================================

def critique_lead(lead: Lead) -> Lead:
    """A second, independent LLM pass whose only job is to check whether
    the Analyst's classification and reason are actually supported by the
    evidence text — not to re-do the classification from scratch. This is
    what catches confident-but-ungrounded ("hallucinated") calls."""
    prompt = f"""Es um revisor cetico. A tua unica funcao e verificar se uma
classificacao feita por outro assistente e realmente justificada pelo
texto fornecido — nao decidas uma classificacao nova do zero.

Texto original:
Titulo: {lead.title}
Texto: {lead.evidence if lead.evidence else "(sem texto disponivel)"}

Classificacao a verificar:
Categoria: {lead.classification}
Score: {lead.score}
Razao dada: {lead.reason}

A razao dada e claramente apoiada pelo texto original, ou e uma
suposicao sem base clara no texto?

Responde APENAS em JSON:
{{"verdict": "confirmed|revised|rejected", "adjusted_score": 0-100, "notes": "uma frase curta explicando a tua decisao"}}

- "confirmed": a razao e claramente apoiada pelo texto, mantem o score.
- "revised": a classificacao tem alguma base mas o score deveria ser
  ajustado (por exemplo, evidencia fraca ou indireta).
- "rejected": a razao nao tem base real no texto — isto parece uma
  suposicao. Usa adjusted_score bem baixo (0-15)."""

    try:
        raw = call_ollama(prompt)
    except requests.RequestException as e:
        lead.critic_verdict = "skipped"
        lead.critic_notes = f"[erro ao contactar Ollama: {e}]"
        return lead

    data = parse_json_loosely(raw)
    lead.critic_verdict = data.get("verdict", "skipped")
    lead.critic_notes = data.get("notes", "").strip()

    try:
        adjusted = int(data.get("adjusted_score", lead.score))
        lead.score = adjusted
    except (TypeError, ValueError):
        pass

    return lead


# ==========================================================================
# Persistence — dedup tracking + CSV output
# ==========================================================================

def load_seen_urls() -> set[str]:
    if not os.path.exists(SEEN_URLS_FILE):
        return set()
    with open(SEEN_URLS_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_seen_url(url: str) -> None:
    with open(SEEN_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def append_leads_to_csv(leads: list[Lead]) -> None:
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "date_found", "classification", "score", "critic_verdict",
                "reason", "critic_notes", "title", "source", "url",
            ])
        for lead in leads:
            writer.writerow([
                time.strftime("%Y-%m-%d"),
                lead.classification,
                lead.score,
                lead.critic_verdict,
                lead.reason,
                lead.critic_notes,
                lead.title,
                lead.source,
                lead.url,
            ])


# ==========================================================================
# Pipeline
# ==========================================================================

def run() -> None:
    seen = load_seen_urls()

    candidates = research_candidates(KEYWORDS)
    new_candidates = [c for c in candidates if c.url not in seen]
    print(f"[pipeline] {len(new_candidates)} new (not seen before)")

    results: list[Lead] = []
    for i, lead in enumerate(new_candidates, 1):
        print(f"[analyst] ({i}/{len(new_candidates)}) {lead.title[:70]}")
        lead.evidence = fetch_article_text(lead.url)
        time.sleep(REQUEST_DELAY)

        lead = analyze_lead(lead)

        if CRITIC_ENABLED and lead.score >= MIN_SCORE_FOR_CRITIC:
            print(f"  -> analyst says {lead.classification} ({lead.score}), sending to critic")
            lead = critique_lead(lead)
        else:
            lead.critic_verdict = "skipped"
            lead.critic_notes = "score below MIN_SCORE_FOR_CRITIC" if CRITIC_ENABLED else "critic disabled"

        results.append(lead)
        append_seen_url(lead.url)

    append_leads_to_csv(results)

    prospects = [l for l in results if l.classification == "prospect" and l.critic_verdict != "rejected"]
    print("\n[done]")
    print(f"  processed:      {len(results)}")
    print(f"  new prospects:  {len(prospects)}")
    print(f"  written to:     {OUTPUT_CSV}")


if __name__ == "__main__":
    run()
