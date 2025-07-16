# 🧠 Rust Server Query Bot

A Discord bot that lets you query Rust game servers for their **player count**, **map link**, **wipe data** and manage a list of saved servers — all via **slash commands**.

---

## 🚀 Features

- `/link` — Save a Rust server by name (`/link Atlas "123.45.67.89:28015"`)
- `/pop` — Check server population (`/pop Atlas`)
- `/map` — Get RustMaps link via BattleMetrics (`/map Atlas`)
- `/wipe` — Placeholder for wipe info (planned feature)
- `/list` — List all linked servers

---

## 🛠️ Requirements

- Python 3.10+
- A Rust server to query (with `A2S` enabled — default Rust behavior)
- A Discord bot token (stored in `.env`)

---

## 🧩 Dependencies

Install using `pip install -r requirements.txt` or manually using this list (virtual enviroment is recommended):

discord.py
python-a2s
python-dotenv
aiohttp
beautifulsoup4