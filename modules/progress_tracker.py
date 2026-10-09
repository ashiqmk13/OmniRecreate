import time

class ProgressTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = None
        self.current_step = "Idle"
        self.step_number = 0
        self.total_steps = 100
        self.progress_percent = 0.0
        self.elapsed_seconds = 0.0
        self.estimated_remaining_seconds = 0.0
        self.logs = []
        self.is_running = False
        self.is_cancelled = False
        self.error_message = None
        self.output_video_path = None

    def start(self, total_steps=100):
        self.reset()
        self.start_time = time.time()
        self.total_steps = total_steps
        self.is_running = True
        self.log("🚀 Generation task initialized.")

    def update(self, current_step_name, progress_percent, detail=None):
        if not self.start_time:
            self.start_time = time.time()
        
        self.current_step = current_step_name
        self.progress_percent = min(100.0, max(0.0, float(progress_percent)))
        self.elapsed_seconds = time.time() - self.start_time
        
        if self.progress_percent > 0:
            total_estimated = (self.elapsed_seconds / self.progress_percent) * 100.0
            self.estimated_remaining_seconds = max(0.0, total_estimated - self.elapsed_seconds)
        else:
            self.estimated_remaining_seconds = 0.0
            
        msg = f"[{self.progress_percent:.1f}%] {current_step_name}"
        if detail:
            msg += f" - {detail}"
        self.log(msg)

    def log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {text}"
        self.logs.append(log_entry)

    def finish(self, output_path=None):
        self.progress_percent = 100.0
        self.elapsed_seconds = time.time() - (self.start_time or time.time())
        self.estimated_remaining_seconds = 0.0
        self.is_running = False
        self.output_video_path = output_path
        self.log(f"✅ Video creation complete! Output saved to {output_path}")

    def fail(self, error):
        self.is_running = False
        self.error_message = str(error)
        self.log(f"❌ Error occurred: {error}")

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def get_status_dict(self):
        return {
            "current_step": self.current_step,
            "progress_percent": round(self.progress_percent, 1),
            "elapsed_time": self.format_time(self.elapsed_seconds),
            "time_remaining": self.format_time(self.estimated_remaining_seconds),
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "remaining_seconds": round(self.estimated_remaining_seconds, 1),
            "is_running": self.is_running,
            "is_cancelled": self.is_cancelled,
            "logs": self.logs[-50:], # return last 50 logs
            "error": self.error_message,
            "output_video_path": self.output_video_path
        }

# Global tracker instance
tracker = ProgressTracker()
