def evaluate_candidate(audio, nlp):
    score = 0
    feedback = []

    # -----------------------------
    # 🎤 AUDIO ANALYSIS
    # -----------------------------

    # 1. Energy (Confidence)
    if audio['energy'] > 0.02:
        score += 20
        feedback.append("Good speaking energy (confident voice)")
    else:
        feedback.append("Speak louder and more confidently")

    # 2. Pitch (Voice variation)
    if 80 < audio['pitch'] < 300:
        score += 20
        feedback.append("Good voice modulation")
    else:
        feedback.append("Improve voice tone (avoid flat voice)")

    # 3. Speech Rate
    if 80 < audio['speech_rate'] < 200:
        score += 20
        feedback.append("Good speaking speed")
    else:
        feedback.append("Maintain proper speaking speed")

    # 4. Clarity (ZCR)
    if audio['zcr'] < 0.1:
        score += 10
        feedback.append("Clear voice quality")
    else:
        feedback.append("Reduce noise / improve clarity")

    # -----------------------------
    # 🧠 NLP ANALYSIS
    # -----------------------------

    # 5. Sentiment (Confidence + positivity)
    if nlp['sentiment'] > 0:
        score += 15
        feedback.append("Positive communication")
    else:
        feedback.append("Try to sound more positive")

    # 6. Answer Length (Content Quality)
    if nlp.get('word_count', 0) > 20:
        score += 15
        feedback.append("Detailed answer")
    else:
        feedback.append("Give more detailed answers")

    # -----------------------------
    # 🧮 FINAL SCORE NORMALIZATION
    # -----------------------------

    if score > 100:
        score = 100

    # -----------------------------
    # 🎯 FINAL RESULT CATEGORY
    # -----------------------------

    if score >= 80:
        result = "Excellent Candidate 🌟"
    elif score >= 60:
        result = "Good Candidate 👍"
    elif score >= 40:
        result = "Average Candidate ⚠️"
    else:
        result = "Needs Improvement ❌"

    return score, result + "\n\n" + "\n".join(feedback)