# Callytics Setup Guide (Low-RAM / 4GB Machine)

This guide walks you through installing Conda, setting up the project, running it, and
using it to analyze call center audio files. Everything runs locally with free, open-source
models -- no API keys or paid services needed.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install Conda](#2-install-conda)
3. [Verify Conda Installation](#3-verify-conda-installation)
4. [Project Setup](#4-project-setup)
5. [Database Setup](#5-database-setup)
6. [Configuration Overview](#6-configuration-overview)
7. [Running the Project](#7-running-the-project)
8. [Using the Project](#8-using-the-project)
9. [Viewing Results](#9-viewing-results)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

Before starting, make sure you have:

- **Operating System**: Linux (Ubuntu/Debian recommended) or macOS
- **RAM**: Minimum 4GB (the project is configured for low-RAM usage)
- **Disk Space**: ~10GB free (for Conda, Python packages, and ML model downloads)
- **Internet**: Required for initial setup (downloading packages and models)
- **ffmpeg**: Required for audio processing

### Install ffmpeg

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update -y
sudo apt install -y ffmpeg build-essential g++
```

**Verify ffmpeg is installed:**
```bash
ffmpeg -version
```

### Install SQLite (usually pre-installed)

**macOS:** Already included.

**Ubuntu/Debian:**
```bash
sudo apt install -y sqlite3
```

---

## 2. Install Conda

Conda manages the Python environment and all dependencies. We recommend **Miniconda**
(lightweight) over Anaconda (large).

### Option A: Miniconda (Recommended)

**macOS (Apple Silicon / M1-M4):**
```bash
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh
```

**macOS (Intel):**
```bash
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh
```

**Linux (x86_64):**
```bash
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh
```

**Linux (ARM64/aarch64):**
```bash
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh
```

### Initialize Conda in your shell

After installing, you need to initialize Conda so it integrates with your terminal:

```bash
~/miniconda3/bin/conda init zsh    # if you use zsh (macOS default)
# OR
~/miniconda3/bin/conda init bash   # if you use bash (Linux default)
```

**Close and reopen your terminal** (or run `source ~/.zshrc` / `source ~/.bashrc`).

### Option B: Using Homebrew (macOS only)

```bash
brew install --cask miniconda
conda init zsh
```

Close and reopen your terminal.

---

## 3. Verify Conda Installation

After reopening your terminal:

```bash
conda --version
```

You should see something like `conda 24.x.x`. If you get "command not found", try:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda --version
```

Useful Conda commands to know:

```bash
conda env list               # List all environments
conda activate <name>        # Activate an environment
conda deactivate             # Deactivate current environment
conda env remove -n <name>   # Delete an environment
```

---

## 4. Project Setup

### Step 4.1: Navigate to the project

```bash
cd /Users/shivam/Desktop/Projects/Test/Callytics
```

### Step 4.2: Create the Conda environment

This reads `environment.yaml` and installs Python 3.11 + all dependencies:

```bash
conda env create -f environment.yaml
```

This will take **5-15 minutes** depending on your internet speed. It installs PyTorch,
NeMo, Whisper, Transformers, and all other libraries.

If the install fails due to memory, try closing other applications first, or install
with pip instead:

```bash
conda create -n Callytics python=3.11 -y
conda activate Callytics
pip install -r requirements.txt
```

### Step 4.3: Activate the environment

```bash
conda activate Callytics
```

Your terminal prompt should now show `(Callytics)` at the beginning. You need to run
this command **every time you open a new terminal** before running the project.

### Step 4.4: Create the input directory

The project watches this directory for new audio files:

```bash
mkdir -p .data/input
```

### Step 4.5: Create a `.env` file

Even though we use all local/free models, the code still loads this file. Create it
with placeholder values:

```bash
cat > .env << 'EOF'
# Not required for local-only setup, but the file must exist.
# Fill these in ONLY if you want to switch to OpenAI/Azure later.
OPENAI_API_KEY=
HUGGINGFACE_TOKEN=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_BASE=
AZURE_OPENAI_API_VERSION=
EOF
```

---

## 5. Database Setup

The project stores results in a SQLite database. Initialize the schema:

```bash
sqlite3 .db/Callytics.sqlite < src/db/sql/Schema.sql
```

If the database file already exists and you want to start fresh:

```bash
rm .db/Callytics.sqlite
sqlite3 .db/Callytics.sqlite < src/db/sql/Schema.sql
```

This creates three tables:
- **Topic** -- detected conversation topics
- **File** -- audio file metadata, features, summary, conflict flag
- **Utterance** -- individual speaker turns with text, sentiment, profanity flags

---

## 6. Configuration Overview

All settings are in `config/config.yaml`. Here's what each section does:

```yaml
runtime:
  device: "cpu"              # "cpu" for no GPU, "cuda" if you have an NVIDIA GPU
  compute_type: "int8"       # "int8" saves memory, "float16" better quality (needs GPU)

whisper:
  model_name: "base"         # Transcription model size: "tiny" (fastest), "base", "small"

models:
  llama:
    model_name: "Qwen/Qwen2.5-0.5B-Instruct"   # Local LLM for text analysis
```

### What you might want to change

| Setting | Current | When to change |
|---------|---------|----------------|
| `whisper.model_name` | `"base"` | Use `"tiny"` if you run out of RAM, `"small"` if you have 6GB+ |
| `models.llama.model_name` | `Qwen/Qwen2.5-0.5B-Instruct` | Use `Qwen/Qwen2.5-1.5B-Instruct` if you have 6GB+ RAM (better quality) |
| `runtime.device` | `"cpu"` | Change to `"cuda"` if you have an NVIDIA GPU |

The NeMo diarization config is at `config/nemo/diar_infer_telephonic.yaml` -- it's already
optimized for low-RAM (small batch sizes, smaller models).

---

## 7. Running the Project

### Start the file watcher

From the project root (make sure the Conda environment is active):

```bash
conda activate Callytics
python main.py
```

You should see output like:

```
Watching directory: .data/input
```

The program is now running and waiting for audio files. It will keep running until you
press `Ctrl+C` to stop it.

### First run: Model downloads

On the **first run**, multiple ML models will be automatically downloaded from Hugging
Face. This is a one-time process:

| Model | Size | Purpose |
|-------|------|---------|
| Faster Whisper `base` | ~150MB | Speech transcription |
| Qwen2.5-0.5B-Instruct | ~1GB | Text analysis (sentiment, summary, etc.) |
| NeMo VAD MarbleNet | ~50MB | Voice activity detection |
| NeMo TitaNet Small | ~80MB | Speaker embeddings |
| NeMo MSDD Telephonic | ~100MB | Speaker diarization |
| NeMo Conformer CTC Small | ~130MB | ASR for diarization |
| MPSENet DNS | ~100MB | Speech enhancement |
| Demucs htdemucs | ~200MB | Vocal separation |
| CTC Forced Aligner | ~300MB | Word-level alignment |
| Deep Punctuation | ~50MB | Punctuation restoration |

Total first-time download: **~2.2GB**. After this, models are cached locally.

---

## 8. Using the Project

### Processing an audio file

While `python main.py` is running in one terminal, open a **second terminal** and drop
an audio file into the input folder:

```bash
# Using the included example file
cp .data/example/en.mp3 .data/input/

# Or copy your own audio file
cp /path/to/your/call-recording.mp3 .data/input/
```

The first terminal will show the pipeline processing in real time:

```
Processing new audio file: .data/input/en.mp3
[SpeechEnhancement] Detected noise level: 0.001234
[SpeechEnhancement] Enhancement with MPSENet started...
...
Final_Output: { ... }
Audio properties inserted successfully into the File table with ID: 1
Utterances inserted successfully into the Utterance table.
```

### What the pipeline does (18 steps)

1. **Dialogue Detection** -- checks if the audio has multiple speakers
2. **Speech Enhancement** -- reduces background noise (MPSENet)
3. **Vocal Separation** -- isolates voices from music/noise (Demucs)
4. **Transcription** -- converts speech to text (Faster Whisper)
5. **Forced Alignment** -- gets word-level timestamps
6. **Diarization** -- identifies who said what (NeMo)
7. **Transcript Processing** -- maps words to speakers, restores punctuation
8. **Write Transcript** -- saves `.txt` and `.srt` subtitle files
9. **Speaker Classification** -- identifies Customer vs CSR roles (LLM)
10. **Sentiment Analysis** -- Positive/Negative/Neutral per sentence (LLM)
11. **Profanity Detection** -- flags profane language (LLM)
12. **Summary** -- one-sentence call summary (LLM)
13. **Conflict Detection** -- was there a disagreement? (LLM)
14. **Topic Detection** -- what was the call about? (LLM)
15. **Audio Feature Extraction** -- MFCC, spectral features, loudness
16. **Silence Calculation** -- total significant silence duration
17. **Database Insert** -- stores everything in SQLite
18. **Cleanup** -- removes temporary files

### Supported audio formats

Any format that ffmpeg supports: `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac`, etc.

### Processing time

On a 4GB RAM CPU-only machine, expect:
- **Short calls (1-2 min):** 5-15 minutes
- **Medium calls (5-10 min):** 15-40 minutes
- **Long calls (30+ min):** 1-2 hours

The LLM steps (9-14) will be the slowest part as the model generates text on CPU.

---

## 9. Viewing Results

### Option A: Query the SQLite database directly

```bash
# Open the database
sqlite3 .db/Callytics.sqlite

# See all processed files
SELECT ID, Name, Duration, Summary, Conflict, Silence FROM File;

# See all utterances from a specific file (replace 1 with the file ID)
SELECT Speaker, Content, Sentiment, Profane FROM Utterance WHERE FileID = 1 ORDER BY Sequence;

# See topic distribution
SELECT t.Name, COUNT(f.ID) as CallCount
FROM File f JOIN Topic t ON f.TopicID = t.ID
GROUP BY t.Name;

# Exit
.quit
```

### Option B: Check the transcript files

After processing, you can find transcript files in `.temp/` (before cleanup):

- `.temp/output.txt` -- plain text transcript with speaker labels
- `.temp/output.srt` -- subtitle format with timestamps

### Option C: Connect Grafana (optional)

For dashboards and visualization, install Grafana and the SQLite plugin:

```bash
# Ubuntu/Debian
sudo apt install -y grafana
sudo grafana-cli plugins install frser-sqlite-datasource
sudo systemctl start grafana-server
```

Then open `http://localhost:3000` (default login: admin/admin), add a SQLite data source
pointing to the `.db/Callytics.sqlite` file, and build dashboards.

---

## 10. Troubleshooting

### "conda: command not found"

Conda isn't in your PATH. Run:
```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate Callytics
```

Or re-initialize:
```bash
~/miniconda3/bin/conda init zsh   # or bash
```
Then restart your terminal.

### Out of memory / killed during processing

Your machine is running out of RAM. Try:

1. Close all other applications (browsers, editors, etc.)
2. Switch to the tiny Whisper model -- edit `config/config.yaml`:
   ```yaml
   whisper:
     model_name: "tiny"
   ```
3. Process shorter audio files (split long files first)

### "No dialogue detected" and file gets deleted

The dialogue detector didn't find speaker turn-taking patterns. This happens with:
- Single-speaker recordings (monologues, voicemails)
- Very short audio files (< 5 seconds)
- Very noisy audio

To process anyway, change `delete_original=True` to `delete_original=False` in
`main.py` line 63.

### NeMo model download fails

NeMo models download from NVIDIA's servers. If it fails:
```bash
# Clear NeMo cache and retry
rm -rf ~/.cache/torch/NeMo
python main.py
```

### "No valid JSON object found in the response"

The small LLM (Qwen 0.5B) sometimes fails to produce valid JSON. The pipeline handles
this with fallback behavior -- results for that step will use defaults. If this happens
frequently, upgrade to a larger model (needs more RAM):
```yaml
models:
  llama:
    model_name: "Qwen/Qwen2.5-1.5B-Instruct"    # needs ~3GB RAM for the model alone
```

### Conda environment creation fails

If `conda env create -f environment.yaml` fails, try the manual approach:
```bash
conda create -n Callytics python=3.11 -y
conda activate Callytics
pip install cython==3.0.11
pip install -r requirements.txt
```

### How to stop the watcher

Press `Ctrl+C` in the terminal where `python main.py` is running.

### How to reprocess a file

The pipeline deletes input files after processing. To reprocess, copy the file into
`.data/input/` again:
```bash
cp .data/example/en.mp3 .data/input/
```

---

## Quick Start (TL;DR)

```bash
# 1. Install Miniconda (one-time)
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3 && rm miniconda.sh
~/miniconda3/bin/conda init zsh && source ~/.zshrc

# 2. Setup project (one-time)
cd /Users/shivam/Desktop/Projects/Test/Callytics
conda env create -f environment.yaml
conda activate Callytics
mkdir -p .data/input
printf 'OPENAI_API_KEY=\nHUGGINGFACE_TOKEN=\n' > .env
sqlite3 .db/Callytics.sqlite < src/db/sql/Schema.sql

# 3. Run (every time)
conda activate Callytics
python main.py

# 4. Process a file (in another terminal)
cp .data/example/en.mp3 .data/input/

# 5. View results
sqlite3 .db/Callytics.sqlite "SELECT ID, Name, Summary FROM File;"
```

---

## REST API Server

Instead of using the file watcher, you can run Callytics as a Django REST API server.

### Start the API server

```bash
conda activate Callytics
python manage.py runserver 8000
```

The server runs at `http://localhost:8000`.

### API Endpoints

#### Submit a file for processing

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/call-recording.mp3"}'
```

Response (HTTP 202):
```json
{
  "id": 1,
  "file_url": "https://example.com/call-recording.mp3",
  "file_name": "call-recording.mp3",
  "status": "pending",
  "error_message": "",
  "created_at": "2026-02-17T10:00:00Z",
  "updated_at": "2026-02-17T10:00:00Z",
  "result": null
}
```

#### Check job status

```bash
curl http://localhost:8000/api/jobs/1/
```

Status values: `pending` → `processing` → `completed` (or `failed`).

#### List all jobs

```bash
curl http://localhost:8000/api/jobs/
```

#### List all call analytics

```bash
curl http://localhost:8000/api/analytics/
```

Returns paginated results with summary, topic, conflict, silence, duration, etc.

#### Get full details for one call

```bash
curl http://localhost:8000/api/analytics/15/
```

Returns full details including all utterances with speaker, text, sentiment, and
profanity flags.
