import anthropic
import json
from datetime import datetime

LEOPOLD_CONTEXT = """
Leopold Aschenbrenner is a former OpenAI researcher (fired in 2024 for alleged leaking)
who wrote the influential 165-page essay "Situational Awareness: The Decade Ahead" (June 2024).
He founded Situational Awareness LP in September 2024, now managing ~$5.52B in US equity positions.
CIK on SEC EDGAR: 0002045724.

His core thesis:
- AGI is likely by 2027-2029, superintelligence shortly after
- The bottleneck is electricity and compute, NOT model development
- This is a national security issue — the US must maintain AI supremacy over China
- Massive investment needed in power infrastructure, data centers, and compute
- His fund bets on: power companies, crypto miners (for cheap power), AI infrastructure

Key people in his circle: Andrej Karpathy, Sam Altman, Eliezer Yudkowsky, Dario Amodei,
Demis Hassabis, Marc Andreessen, Nathan Benaich, David Cahn (Sequoia), Zvi Mowshowitz.
"""

DAILY_PROMPT = """You are a research analyst producing a daily intelligence brief.

Context about the subject:
{context}

Today's scraped data from all sources:
{data}

Produce a concise daily brief (300-500 words) called "The Leo Brief" covering ONLY new information from the last 24 hours.
If nothing significant happened, say so clearly — do not pad.

Structure:
## Leopold Directly
What did Leopold post/say today? Any fund activity or news about him personally?

## His Circle
What are the key people in his orbit saying that connects to his thesis? Only notable items.

## Market Signal
Any new SEC filings, position changes, or market moves in his known investment areas?

## Community Pulse
What is Reddit/HN/LessWrong saying? Any viral discussion about his ideas?

## Counterpoint
One skeptic voice or contrary datapoint worth noting. If none, skip this section.

Date: {date}
Be direct, no fluff. Use bullet points where appropriate.
"""

WEEKLY_PROMPT = """You are a senior research analyst producing a comprehensive weekly intelligence report.

Context about the subject:
{context}

Full week of scraped data (last 7 days):
{data}

Produce a detailed weekly report (1500-2500 words) called "The Leo Deep Dive" for the week ending {date}.

Structure:
## Executive Summary
3-5 bullet points: the most important things that happened this week

## Leopold Aschenbrenner — Full Week Activity
Everything he posted, said, or was reported about. Analyze tone and themes.

## Situational Awareness LP — Fund Intelligence
Any SEC filings, position changes, analyst coverage, or market signals about the fund's holdings.
Reference known thesis areas: power companies, compute infrastructure, crypto miners.

## The Circle — Key Voices This Week
What Karpathy, Altman, Yudkowsky, Amodei, Andreessen and others said.
Focus on anything that confirms, challenges, or extends Leopold's thesis.

## Academic & Research Signals
New ArXiv papers or research relevant to his AGI timeline thesis.

## Community & Market Sentiment
Reddit/HN/LessWrong discussion. Is conviction in his thesis growing or weakening?
Any new converts or prominent critics?

## Media Coverage
Notable press coverage this week.

## Thesis Check
How does this week's information update our view of Leopold's core thesis?
What would confirm or falsify it?

## What To Watch Next Week
2-3 specific things to monitor.

Be analytical, not just descriptive. Connect dots across sources.
"""

def build_daily_brief(all_data: list[dict], api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    data_str = json.dumps(all_data, indent=2, default=str)[:80000]  # token safety cap

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="You are a sharp, concise research analyst. Write in clear, direct prose.",
        messages=[{
            "role": "user",
            "content": DAILY_PROMPT.format(
                context=LEOPOLD_CONTEXT,
                data=data_str,
                date=datetime.utcnow().strftime("%B %d, %Y"),
            )
        }]
    )
    return message.content[0].text

def build_weekly_report(all_data: list[dict], api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    data_str = json.dumps(all_data, indent=2, default=str)[:120000]  # larger cap for weekly

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        system="You are a senior research analyst writing for a sophisticated investor audience.",
        messages=[{
            "role": "user",
            "content": WEEKLY_PROMPT.format(
                context=LEOPOLD_CONTEXT,
                data=data_str,
                date=datetime.utcnow().strftime("%B %d, %Y"),
            )
        }]
    )
    return message.content[0].text
