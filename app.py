import os
import time
import threading
import gradio as gr
from config import OUTPUT_DIR, DEFAULT_SETTINGS
from modules.progress_tracker import tracker
from pipeline import VideoRecreationPipeline

pipeline_instance = VideoRecreationPipeline()

def run_recreation_wrapper(
    sample_video,
    visual_instructions,
    target_duration,
    lock_facial_features,
    character_ref,
    voice_engine,
    voice_name,
    subtitle_style
):
    """Starts video recreation thread and yields status updates for Gradio UI."""
    sample_video_path = sample_video.name if sample_video else None
    character_ref_path = character_ref.name if character_ref else None

    # Run in background thread
    def thread_target():
        pipeline_instance.run_recreation(
            sample_video_path=sample_video_path,
            visual_instructions=visual_instructions,
            target_duration_minutes=int(target_duration),
            lock_facial_features=lock_facial_features,
            character_reference_path=character_ref_path,
            voice_engine=voice_engine,
            voice_name=voice_name,
            subtitle_style=subtitle_style,
            output_filename=f"video_recreated_{int(time.time())}.mp4"
        )

    t = threading.Thread(target=thread_target)
    t.start()

    # Generator loop to update live UI progress bar, percentage, elapsed, and remaining time
    while t.is_alive() or tracker.is_running:
        status = tracker.get_status_dict()
        pct = status["progress_percent"]
        current_step = status["current_step"]
        elapsed = status["elapsed_time"]
        remaining = status["time_remaining"]
        logs_text = "\n".join(status["logs"][-15:])

        progress_md = f"""
### ⚙️ Progress: **{pct:.1f}%**
**Current Action:** `{current_step}`  
⏱️ **Elapsed Time:** `{elapsed}` &nbsp;|&nbsp; ⌛ **Time Left (Est.):** `{remaining}`
"""
        yield (
            gr.update(value=pct / 100.0, visible=True),
            gr.update(value=progress_md),
            gr.update(value=logs_text),
            None # Video output stays None until done
        )
        time.sleep(0.5)

    t.join()
    status = tracker.get_status_dict()
    logs_text = "\n".join(status["logs"][-20:])
    final_output = status.get("output_video_path")

    if final_output and os.path.exists(final_output):
        progress_md = f"""
### ✅ **Video Creation Complete!**
⏱️ **Total Time:** `{status['elapsed_time']}`  
Output generated with **STRICT NO MUSIC** & **{'Faceless Human Features' if lock_facial_features else 'Unlocked Face Generation'}**.
"""
        yield (
            gr.update(value=1.0, visible=True),
            gr.update(value=progress_md),
            gr.update(value=logs_text),
            final_output
        )
    else:
        err = status.get("error", "Unknown error")
        progress_md = f"### ❌ Task Failed: {err}"
        yield (
            gr.update(value=0.0, visible=True),
            gr.update(value=progress_md),
            gr.update(value=logs_text),
            None
        )


# Custom Premium Dark Glassmorphism CSS
custom_css = """
body {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.gradio-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
}
.panel-box {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}
.accent-button {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}
.accent-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}
.lock-banner {
    background: rgba(234, 179, 8, 0.15);
    border: 1px solid rgba(234, 179, 8, 0.3);
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 12px;
}
"""

def build_ui():
    with gr.Blocks(title="OmniRecreate AI - Video Studio", css=custom_css, theme=gr.themes.Soft(dark_mode=True)) as demo:
        gr.Markdown(
            """
            # 🎬 **OmniRecreate AI - Universal Video Studio**
            ### Recreate Videos of Any Length | Open-Source Engine | Zero Music Enforcement | Facial Feature Lock Switch
            """
        )

        with gr.Row():
            # Left Column: Inputs & Controls
            with gr.Column(scale=1, elem_classes=["panel-box"]):
                gr.Markdown("### 📥 1. Sample Video & Script Inputs")
                sample_video_input = gr.File(
                    label="Upload Sample Video (Optional - for auto transcription & style matching)",
                    file_types=[".mp4", ".mkv", ".mov", ".avi", ".webm"]
                )
                visual_instructions_input = gr.Textbox(
                    label="Visual Instructions & Content Prompt",
                    placeholder="Describe the target video content, visuals, aesthetic, or topic...",
                    lines=4
                )
                
                gr.Markdown("### 🔒 2. Human & Character Feature Controls")
                with gr.Group():
                    lock_facial_switch = gr.Checkbox(
                        label="🔒 Lock Facial Features (Default: LOCKED)",
                        value=True,
                        info="When LOCKED: Generated video humans will NEVER have facial features (faceless mannequin / silhouette style). When UNLOCKED: Allows facial features."
                    )
                    character_ref_input = gr.File(
                        label="Character Reference Image (Optional)",
                        file_types=[".jpg", ".png", ".webp"],
                        info="Ensures all generated humans/silhouettes follow this character design."
                    )

                gr.Markdown("### ⏱️ 3. Video Output Configuration")
                target_duration_slider = gr.Slider(
                    minimum=1,
                    maximum=60,
                    value=5,
                    step=1,
                    label="Target Video Duration (Minutes)",
                    info="Supports creating videos of any length (e.g. 5m, 15m, 25m, 60m...)"
                )
                
                with gr.Accordion("⚙️ Audio & Subtitle Advanced Settings", open=False):
                    gr.Markdown("🚫 **Music Policy:** STRICTLY LOCKED - No background music will ever be added.")
                    voice_engine_dropdown = gr.Dropdown(
                        choices=["kokoro", "chatterbox", "edge_tts", "pyttsx3"],
                        value="kokoro",
                        label="Voice TTS Engine (Open-Source)"
                    )
                    voice_name_input = gr.Textbox(
                        value="af_heart",
                        label="Kokoro Voice ID",
                        info="Options: af_heart, am_adam, af_bella, am_michael"
                    )
                    subtitle_style_dropdown = gr.Dropdown(
                        choices=["bold_yellow", "cyber_cyan", "minimal_white"],
                        value="bold_yellow",
                        label="Text Subtitle Style Effect"
                    )

                generate_btn = gr.Button("🚀 Generate Recreated Video", elem_classes=["accent-button"])

            # Right Column: Live Progress & Output Player
            with gr.Column(scale=1, elem_classes=["panel-box"]):
                gr.Markdown("### 📊 Live Processing Dashboard")
                
                progress_bar = gr.Progress(track_tqdm=False)
                progress_status_md = gr.Markdown("### Ready to generate.")
                
                logs_textbox = gr.Textbox(
                    label="Live Console Logs",
                    interactive=False,
                    lines=10,
                    max_lines=15
                )

                gr.Markdown("### 📺 Recreated Master Video Output (No Music)")
                video_output_player = gr.Video(
                    label="Final Output Video (Video + Audio + SFX + Text Effects)",
                    interactive=False
                )

        # Trigger logic
        generate_btn.click(
            fn=run_recreation_wrapper,
            inputs=[
                sample_video_input,
                visual_instructions_input,
                target_duration_slider,
                lock_facial_switch,
                character_ref_input,
                voice_engine_dropdown,
                voice_name_input,
                subtitle_style_dropdown
            ],
            outputs=[
                progress_bar,
                progress_status_md,
                logs_textbox,
                video_output_player
            ]
        )

    return demo

if __name__ == "__main__":
    app = build_ui()
    # share=True provides a free public URL on Google Colab!
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)
