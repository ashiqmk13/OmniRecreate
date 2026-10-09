# 🎬 OmniRecreate AI - Open Source Video Recreation Studio

> **Recreate videos of any length (5 min, 15 min, 25 min+) with Open-Source AI models, Zero API cost, Strict NO MUSIC enforcement, Facial Feature Lock switch, Character Reference consistency, and dynamic Text Effects.**

---

## ✨ Features

- 📹 **Recreate Videos of Any Length**: Generate multi-scene video recreations ranging from short clips to 25+ minute long videos.
- 📥 **Sample Video & Visual Instruction Analysis**: Transcribes audio via Faster-Whisper, analyzes keyframe visual style, contrast, and color palette, and generates a structured script matching your requirements.
- 🔒 **Facial Feature Lock & Character Reference**:
  - **LOCKED (Default)**: AI generates humans as faceless mannequins, smooth silhouettes, or anonymous stylized figures with **zero facial features**.
  - **UNLOCKED**: Toggle switch allows standard human facial feature generation.
  - **Character Reference Image**: Upload a reference image to keep human/silhouette outfits, colors, and postures consistent across every scene.
- 🎙️ **Open-Source TTS Voice Synthesis**: Supports **Kokoro-TTS** (82M ultra-fast open source voice synthesis), **Chatterbox**, Edge-TTS, and system TTS.
- 🔊 **Sound Effects (SFX) Generator**: Automatically generates and syncs cinematic sound effects (booms, swooshes, tech hums, risers) per scene.
- 🚫 **STRICT NO MUSIC POLICY**: Background music is strictly excluded from audio mixing to guarantee clean voice + SFX stems.
- ✍️ **Dynamic Text Effects & Subtitles**: Custom styled animated captions (Bold Yellow, Cyber Cyan, Minimal White).
- 📊 **Real-time Progress Dashboard**: Displays progress percentage (%), current step, time elapsed, and estimated time remaining (ETA) with live console logs.
- ☁️ **Google Colab & Local Ready**: 100% runnable on local machines or Google Colab with auto model caching.

---

## 🚀 Quick Start Guide (Local Execution)

### Prerequisites
- Python 3.9+
- FFmpeg installed and added to system PATH.

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/omnirecreate-ai.git
cd omnirecreate-ai

# Install dependencies
pip install -r requirements.txt
```

### Launch Web UI
```bash
python app.py
```
Open your browser at `http://localhost:7860`.

---

## ☁️ Google Colab Setup (1-Click Run)

1. Upload this repository to your GitHub.
2. Open [Google Colab](https://colab.research.google.com/) and create a new notebook or open `colab_launcher.ipynb`.
3. Set runtime to **GPU** (T4 / V100 / A100).
4. Run the launcher cell:
   ```bash
   !git clone https://github.com/YOUR_USERNAME/omnirecreate-ai.git
   %cd omnirecreate-ai
   !python setup_colab.py
   ```
5. Click the `.gradio.live` link generated in the output to access your private studio!

---

## 📁 Repository Architecture

```
omnirecreate-ai/
├── app.py                      # Gradio Web GUI Application
├── setup_colab.py              # Auto-setup & model pre-cacher for Google Colab
├── colab_launcher.ipynb        # 1-Click Jupyter Notebook for Colab
├── pipeline.py                 # Core video generation pipeline
├── config.py                   # System configuration & prompt rules
├── requirements.txt            # Python dependencies
├── modules/
│   ├── transcriber.py          # Faster-Whisper audio extraction & transcription
│   ├── style_analyzer.py       # Keyframe computer vision & style profiling
│   ├── script_writer.py        # Multi-scene script breakdown engine for any length
│   ├── tts_engine.py           # Kokoro-TTS & open-source speech synthesizer
│   ├── sfx_engine.py           # Procedural sound effect synthesizer
│   ├── text_effects.py         # Subtitle & kinetic text generator (.ass format)
│   ├── visual_generator.py     # AI Visual generator with Facial Lock & Char Ref
│   ├── compositor.py           # FFmpeg video/audio/sfx stitcher (No music)
│   └── progress_tracker.py     # Real-time percentage & ETA calculator
└── output/                     # Exported video files
```

---

## 📜 License
Open Source under MIT License. No proprietary APIs, no hidden costs.
