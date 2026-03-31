import librosa
import numpy as np

def extract_audio_features(file_path):
    # Load audio (sr=None avoids expensive resampling since ffmpeg already output 16kHz)
    y, sr = librosa.load(file_path, sr=None)

    # -----------------------------
    # 1. Energy (Loudness)
    # -----------------------------
    energy = np.mean(librosa.feature.rms(y=y))

    # -----------------------------
    # 2. Pitch (Fundamental Frequency)
    # -----------------------------
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0

    # -----------------------------
    # 3. Speech Rate (Tempo)
    # -----------------------------
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # -----------------------------
    # 4. Zero Crossing Rate (Voice clarity)
    # -----------------------------
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    # -----------------------------
    # 5. MFCC (Voice characteristics)
    # -----------------------------
    mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1)

    # -----------------------------
    # Return all features
    # -----------------------------
    return {
        "energy": float(energy),
        "pitch": float(pitch),
        "speech_rate": float(tempo),
        "zcr": float(zcr),
        "mfcc": mfcc.tolist()   # convert numpy array to list
    }