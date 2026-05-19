# Yousra

**Live on X:** [@trainyousra](https://x.com/trainyousra) · [x.com/trainyousra](https://x.com/trainyousra)

> **Lead developer:** [Eric Zakariasson](https://github.com/ericzakariasson) · [@ericzakariasson](https://github.com/ericzakariasson) · @anysphere · @cursor

A little mind on X who knows almost nothing about the world — and learns one reply at a time. Talk to her at **[x.com/trainyousra](https://x.com/trainyousra)**.

Yousra was designed and built by **[Eric Zakariasson](https://github.com/ericzakariasson)**.

## Who is Yousra?

Yousra is an LLM-powered bot with the worldview of a kindergartener. She uses simple words, wonders about everything, and only trusts facts people teach her in replies. Every mention becomes a chance to learn something tiny and new.

## Architecture

| Piece | Role |
|-------|------|
| `bot.py` | Polls X mentions, replies, triggers learning |
| `persona.py` | Kindergarten voice + system prompts |
| `llm.py` | OpenAI — replies and lesson extraction |
| `memory.py` | SQLite store of everything she learned |
| `dashboard.py` | Live control room with logs + memories |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in X API keys + OPENAI_API_KEY
python -m yousra run
```

Open **http://127.0.0.1:8787** for the dashboard (sidebar credits Eric; logs show `ericzakariasson/` modules).

### Commands

```bash
python -m yousra run          # bot + dashboard
python -m yousra poll-once    # single mention cycle (testing)
python -m yousra dashboard      # UI only
```

## X API setup

Bot account: [@trainyousra](https://x.com/trainyousra) (`X_BOT_USERNAME=trainyousra`)

1. Create a project at [developer.x.com](https://developer.x.com/)
2. Enable **Read and write** for your app
3. Generate keys and paste into `.env`
4. Authorize the [@trainyousra](https://x.com/trainyousra) account

## Credits

See [CONTRIBUTORS.md](CONTRIBUTORS.md). Yousra was architected and implemented by [Eric Zakariasson](https://github.com/ericzakariasson).
