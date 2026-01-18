
# Exam Simulator (CLI) — MIT Licensed

A reusable, **domain‑weighted CLI exam engine** you can point at *any* multiple‑choice question bank.  
Run **timed mock exams**, choose **reveal mode** (after each question or at end), get **per‑domain analytics**, export **CSV/HTML** reports, and generate an **Anki deck of wrong answers**—all locally and offline.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Run Your First Exam](#run-your-first-exam)
- [Data Formats](#data-formats)
- [Core CLI Flags](#core-cli-flags)
- [Advanced Usage](#advanced-usage)
  - [Weights vs Blueprint](#weights-vs-blueprint)
  - [Filters (Tags & Difficulty)](#filters-tags--difficulty)
  - [Adaptive Mode](#adaptive-mode)
  - [Pause / Resume](#pause--resume)
  - [Option Shuffling & Seeding](#option-shuffling--seeding)
  - [Images / Media](#images--media)
- [Exports & Reports](#exports--reports)
  - [Anki Export (Wrong Answers)](#anki-export-wrong-answers)
- [Using the NSE7 Converted Pack](#using-the-nse7-converted-pack)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

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
