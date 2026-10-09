import sys
import os
import subprocess

def run_cmd(cmd):
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Warning: Command '{cmd}' exited with code {res.returncode}")

def setup_environment():
    print("==================================================")
    print("🚀 OmniRecreate AI - Google Colab Setup Initializer")
    print("==================================================")
    
    # 1. Update package managers & install ffmpeg
    print("📦 Step 1: Installing system ffmpeg & audio packages...")
    run_cmd("apt-get update -qq && apt-get install -y -qq ffmpeg libasound2-dev espeak-ng")
    
    # 2. Install Python requirements
    print("🐍 Step 2: Installing Python open-source dependencies...")
    run_cmd(f"{sys.executable} -m pip install -q -r requirements.txt")

    # 3. Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"⚡ GPU Detected: {gpu_name} (Acceleration enabled)")
        else:
            print("⚠️ No CUDA GPU detected. Running in optimized CPU mode.")
    except Exception as e:
        print(f"PyTorch check note: {e}")

    # 4. Pre-download / Cache Kokoro & Whisper models to save execution time
    print("🧠 Step 3: Pre-caching open-source AI weights...")
    try:
        from faster_whisper import WhisperModel
        print(" -> Pre-loading Whisper speech model...")
        WhisperModel("small", compute_type="int8", download_root="./models/whisper")
    except Exception as e:
        print(f"Pre-cache whisper note: {e}")

    print("==================================================")
    print("✅ Setup complete! Launching Web UI studio...")
    print("==================================================")
    
    run_cmd(f"{sys.executable} app.py")

if __name__ == "__main__":
    setup_environment()
