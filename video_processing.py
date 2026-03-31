import os
import subprocess
import imageio_ffmpeg

def extract_audio(video_path):
    try:
        # -----------------------------
        # 1. Check file exists
        # -----------------------------
        if not os.path.exists(video_path):
            return "Video file not found"

        # -----------------------------
        # 2. Define output audio path
        # -----------------------------
        audio_path = video_path.replace(".webm", ".wav")

        # -----------------------------
        # 3. Get safe ffmpeg exe & build command
        # -----------------------------
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        command = [
            ffmpeg_exe,
            "-y",
            "-i", video_path,
            "-t", "90",
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ]

        # -----------------------------
        # 4. Run command
        # -----------------------------
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # -----------------------------
        # 5. Validate output
        # -----------------------------
        if not os.path.exists(audio_path):
            return "Audio extraction failed"

        return audio_path

    except Exception as e:
        return f"Error: {str(e)}"