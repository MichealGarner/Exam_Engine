# Exam Simulator (CLI) — MIT Licensed

A reusable, **domain‑weighted CLI exam engine** you can point at *any* multiple‑choice question bank.  
Run **timed mock exams**, choose **reveal mode** (after each question or at end), get **per‑domain analytics**, export **CSV/HTML** reports, and generate an **Anki deck of wrong answers**—all locally and offline.

---

## Table of Contents

- #features
- #quick-start
- #installation
- #run-your-first-exam
- #data-formats
- #core-cli-flags
- #advanced-usage
  - #weights-vs-blueprint
  - #filters-tags--difficulty
  - #adaptive-mode
  - #pause--resume
  - #option-shuffling--seeding
  - #images--media
- #exports--reports
  - #anki-export-wrong-answers
- #using-the-nse7-converted-pack
- #project-structure
- #troubleshooting
- #contributing
- #license

---

## Features

- **Domain‑weighted selection** *(or strict section blueprint if you need exact counts per domain)*  
- **Timer** in the header + **live countdown ticker** (`--live-timer`) and **terminal bell** at threshold (`--beep-threshold`)
- **Reveal mode:** show correct answers **after** each question or only **at the end**
- **Option shuffling** (and deterministic runs with `--seed`)
- **Filters:** by `tags` and `difficulty`
- **Adaptive mode:** bias selection *during* the exam toward domains you’re missing
- **Pause / Resume**: press `P` to save state; resume with `--resume`
- **Multi‑user** history via `--user` (each user gets their own history file)
- **Reports:** CSV & HTML after each run
- **Anki Export (NEW):** `--export-anki-wrong` creates an Anki‑ready CSV of the items you missed
- Works **offline**, cross‑platform (**Windows / macOS / Linux**)

---

## Quick Start

> **Prerequisite:** Python 3.9+ (no admin rights required)

```bash
# 1) From the repo root (e.g., exam_engine_full/), create a virtual environment
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
source .venv/bin/activate

# 2) Install runtime dependencies
pip install -r requirements.txt

# 3) Run an exam (with all UX enabled)
python -m engine.main \
  --num-questions 40 \
  --time-limit 75 \
  --reveal after \
  --shuffle --shuffle-options \
  --live-timer --open-images \
  --seed 42 \
  --user micheal
```

After the session, check `results/` for your **history JSON**, **CSV**, **HTML** (and optionally **Anki CSV** if you enable that flag; see below).

---

## Installation

1. **Clone or unzip** the repository so that you have the `exam_engine_full/` folder locally.
2. Create a **virtual environment** and **activate** it:
   - **Windows (PowerShell)**
     ```powershell
     py -3 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure your **data** files are in `./data/` (see #data-formats).

---

## Run Your First Exam

Minimal run:
```bash
python -m engine.main
```

Typical run with UX features and deterministic shuffling:
```bash
python -m engine.main \
  --num-questions 40 \
  --time-limit 75 \
  --reveal after \
  --shuffle --shuffle-options \
  --live-timer \
  --seed 42
```

A final-review exam and Anki export:
```bash
python -m engine.main \
  --num-questions 40 \
  --reveal end \
  --export-anki-wrong
```

---

## Data Formats

Place data files in **`./data/`** (default). You can override with `--data-dir`.

### `questions.jsonl` (one JSON object per line)
```json
{"id": 1,
 "domain": "VPN",
 "type": "mcq",
 "question": "**Packet flow over IPsec**: Which policy is matched first when a LAN host sends to a remote subnet over IPsec?",
 "options": {"A":"Local-in policy","B":"IPv4 policy referencing the IPsec interface","C":"Proxy-policy only","D":"Implicit deny"},
 "answer": "B",
 "answer_text": "Traffic matches the IPv4 policy on egress towards the IPsec interface.",
 "tags": ["ipsec","policy"],
 "difficulty": 2,
 "media": ["images/ipsec_flow.png"]}
```

### `metadata.json`
```json
{
  "title": "Your Exam Title",
  "domains": {
    "VPN": 0.25,
    "Routing": 0.20,
    "Security Profiles": 0.20,
    "System Troubleshooting": 0.15,
    "Authentication": 0.10,
    "Fabric & HA": 0.10
  },
  "notes": "Weights can be overridden with --weights"
}
```

### Optional: `blueprint.json`
```json
{ "VPN": 10, "Routing": 8, "Security Profiles": 8, "System Troubleshooting": 6, "Authentication": 4, "Fabric & HA": 4 }
```

---

## Core CLI Flags

- `--num-questions 40` — number of questions to include
- `--time-limit 75` — timer in minutes
- `--reveal after|end` — immediate feedback **after** each question or only **at end**
- `--shuffle` — shuffle final selection
- `--shuffle-options` — shuffle choices A/B/C/D
- `--seed 42` — make your shuffles reproducible
- `--data-dir ./data` — set a custom data directory
- `--questions-file questions.jsonl` / `--metadata-file metadata.json` — custom filenames
- `--user micheal` — per‑user history file in `results/history_<user>.json`
- `--live-timer` — live countdown ticker
- `--beep-threshold 5` — minutes remaining that triggers a terminal bell

---

## Advanced Usage

### Weights vs Blueprint
- **Weights** (from `metadata.json` or `--weights`) distribute a total across domains *proportionally*.  
  Example:
  ```bash
  python -m engine.main --num-questions 60 \
    --weights "VPN:0.25,Routing:0.20,Security Profiles:0.20,System Troubleshooting:0.15,Authentication:0.10,Fabric & HA:0.10"
  ```
- **Blueprint** enforces **exact counts per domain**:
  ```bash
  python -m engine.main --blueprint path/to/blueprint.json
  ```

### Filters (Tags & Difficulty)
- **Tags**:
  - Include: `--include-tags "bgp,ospf"`
  - Exclude: `--exclude-tags "ssl"`
- **Difficulty**:
  - `--min-difficulty 2 --max-difficulty 4` *(if your questions specify `difficulty` 1..5)*

### Adaptive Mode
Enable **in-run adaptation** (bias the next pick toward domains you’re currently missing):
```bash
python -m engine.main --adaptive
```

### Pause / Resume
- Press **`P`** when prompted for an answer to pause/save (state written to `--save-state` path if provided).
- Resume later:
  ```bash
  python -m engine.main --resume results/session_state.json
  ```

### Option Shuffling & Seeding
- Shuffle choices with `--shuffle-options`
- Use `--seed <int>` for deterministic exam and option order.

### Images / Media
- If a question includes `"media": ["images/diagram.png"]`, pass `--open-images` to open linked images via your OS (Windows/macOS/Linux) when the question is shown.

---

## Exports & Reports

After each run the engine writes:

- **History JSON** → `results/history_<user>.json`
- **CSV Summary** → `results/<timestamp>_summary.csv`
- **HTML Summary** → `results/<timestamp>_summary.html`

### Anki Export (Wrong Answers)
**New:** add `--export-anki-wrong` to write an **Anki‑ready CSV** containing only the questions you missed:

- **Auto filename** in `results/<timestamp>_anki_wrong.csv`:
  ```bash
  python -m engine.main --num-questions 40 --reveal after --export-anki-wrong
  ```
- **Custom path**:
  ```bash
  python -m engine.main --num-questions 40 --reveal after --export-anki-wrong results/my_wrong_anki.csv
  ```

**CSV columns:**
- **Front**: question + the A/B/C/D options (with `<br>` line breaks for a clean Anki card)
- **Back**: `Correct: <letter> — <rationale>`
- **Tags**: sanitized domain (e.g., `Security_Profiles`, `Fabric_and_HA`)

Import this CSV to Anki (Basic note type works well); cards will have the question on the front and the correct answer + rationale on the back.

---

## Using the NSE7 Converted Pack

If you have the **NSE7 converted question pack**:

1. Unzip it and copy its **`data/`** folder into the engine root (so you have `exam_engine_full/data/...`).
2. Run the engine:
   ```bash
   python -m engine.main --num-questions 60 --time-limit 90 \
     --reveal end --shuffle --shuffle-options --open-images --live-timer \
     --user micheal
   ```

> You can keep private question banks out of Git by not committing `data/` (or use a `.gitignore` entry for it).

---

## Project Structure

```
exam_engine_full/
├─ data/
│  ├─ questions.jsonl
│  ├─ metadata.json
│  └─ images/
├─ engine/
│  ├─ __init__.py
│  ├─ analytics.py
│  ├─ exam.py
│  ├─ loader.py
│  ├─ main.py           # entry: python -m engine.main [flags]
│  ├─ models.py
│  ├─ renderer.py
│  ├─ selector.py
│  └─ timer.py
├─ results/
│  └─ history_<user>.json
├─ README.md
├─ requirements.txt
└─ LICENSE
```

---

## Troubleshooting

- **`ModuleNotFoundError: rich`**  
  You likely skipped `pip install -r requirements.txt`. Activate your venv and install.

- **“No questions after applying filters”**  
  Remove or relax `--include-tags/--exclude-tags` and `--min-difficulty/--max-difficulty`.

- **Images don’t open**  
  Use `--open-images` and ensure paths in `media` exist under `./data/`.

- **Terminal bell not audible**  
  Some terminals suppress it. You can still see the time left in the header or use `--live-timer`.

---

## Contributing

PRs welcome! If you add features, please:
- Keep code **well‑commented**
- Stick to **PEP‑8-ish** style
- Add small unit tests where relevant (loader/selector/analytics are good candidates)
- Propose flags with meaningful names and help text

---

## License

This project is released under the **MIT License**.  
See LICENSE for details.
