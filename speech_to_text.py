from faster_whisper import WhisperModel
import os
import wave
import threading

# Lazy-load the model to prevent startup crashes on Railway
model = None

def get_whisper_model():
    global model
    if model is None:
        print("[STT] Loading faster-whisper tiny model (LAZY LOAD)...")
        # cpu mode, INT8 quantization = very low RAM usage
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("[STT] faster-whisper tiny model loaded.")
    return model

MAX_AUDIO_SECONDS = 90  # Never transcribe more than 90 seconds


def _trim_audio(src_path, dst_path, max_seconds):
    """Trim WAV to max_seconds. Returns dst_path (or src_path if trim not needed)."""
    try:
        with wave.open(src_path, 'rb') as wf:
            fr = wf.getframerate()
            total_frames = wf.getnframes()
            max_frames = fr * max_seconds
            if total_frames <= max_frames:
                return src_path          # no trimming needed
            wf.rewind()
            frames = wf.readframes(max_frames)
            params = wf.getparams()

        with wave.open(dst_path, 'wb') as out:
            out.setparams(params)
            out.writeframes(frames)
        return dst_path
    except Exception:
        return src_path   # fallback to original on any error


def transcribe_audio(file_path, timeout_seconds=90):
    """
    Transcribes audio using faster-whisper tiny model.
    Trims audio to MAX_AUDIO_SECONDS before processing.
    Times out after timeout_seconds to prevent hanging.
    """
    try:
        if not os.path.exists(file_path):
            return "Audio file not found"

        # Trim to 90s so model doesn't chew through silence
        trimmed_path = file_path.replace(".wav", "_trimmed.wav")
        audio_to_process = _trim_audio(file_path, trimmed_path, MAX_AUDIO_SECONDS)

        result_holder = [None]
        error_holder  = [None]

        def _run():
            try:
                whisper_model = get_whisper_model()
                segments, _ = whisper_model.transcribe(
                    audio_to_process,
                    language="en",
                    beam_size=1      # Fastest setting
                )
                result_holder[0] = " ".join([seg.text for seg in segments])
            except Exception as e:
                error_holder[0] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=timeout_seconds)

        # Clean up trimmed file
        if os.path.exists(trimmed_path) and trimmed_path != file_path:
            try: os.remove(trimmed_path)
            except: pass

        if t.is_alive():
            return "No meaningful speech detected."

        if error_holder[0]:
            return f"Error in transcription: {error_holder[0]}"

        text = (result_holder[0] or "").strip()
        return text if text else "No speech detected"

    except Exception as e:
        return f"Error in transcription: {str(e)}"