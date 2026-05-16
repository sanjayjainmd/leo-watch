# Leo Watch

Daily and weekly intelligence tracking for Leopold Aschenbrenner, Situational Awareness LP,
and the broader AGI investing circle.

## What It Does

- **Daily (Mon–Fri, 7am ET)** — "The Leo Brief": short summary of new information only
- **Weekly (Sunday, 6pm ET)** — "The Leo Deep Dive": comprehensive week-in-review report

Both are emailed automatically via GitHub Actions.

## Sources

| Platform | What |
|----------|------|
| Twitter/X | 13 tracked handles (Leopold + circle) |
| Reddit | r/singularity, r/MachineLearning, r/artificial, r/LessWrong, r/AIInvesting, r/stocks |
| YouTube | Lex Fridman, Dwarkesh Patel, 80K Hours, BG2 Pod |
| LinkedIn | Fund and professional announcements |
| Hacker News | Keyword mentions |
| Google News | Press coverage |
| Substack | Zvi, Nathan Benaich, Rohit Krishnan, Packy McCormick |
| SEC EDGAR | Situational Awareness LP (CIK 0002045724) + Coatue, ARK |
| ArXiv | AGI/compute research papers |

## Setup

### 1. Clone and configure
```bash
git clone https://github.com/YOUR_USERNAME/leo-watch.git
cd leo-watch
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
python main.py daily   # run daily brief
python main.py weekly  # run weekly report
```

### 4. GitHub Secrets
Add these secrets to your GitHub repo (Settings → Secrets → Actions):

| Secret | Value |
|--------|-------|
| `APIFY_API_KEY` | From apify.com |
| `ANTHROPIC_API_KEY` | From console.anthropic.com |
| `SENDER_EMAIL` | Your Gmail address |
| `SENDER_PASSWORD` | Gmail app password (not your login password) |
| `RECIPIENT_EMAIL` | Where to send the digest |

### Gmail App Password
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification if not already on
3. Search "App passwords" → create one named "Leo Watch"
4. Use that 16-character password as `SENDER_PASSWORD`

## Tracked Twitter Handles
- @leopoldasch — Leopold Aschenbrenner
- @karpathy — Andrej Karpathy
- @sama — Sam Altman
- @ESYudkowsky — Eliezer Yudkowsky
- @DarioAmodei — Dario Amodei
- @demishassabis — Demis Hassabis
- @pmarca — Marc Andreessen
- @nathanbenaich — Nathan Benaich
- @DavidCahn6 — David Cahn (Sequoia)
- @GaryMarcus — Gary Marcus (skeptic/counterpoint)
- @robbensinger — Rob Bensinger
- @scottaaronson — Scott Aaronson
- @TheZvi — Zvi Mowshowitz
