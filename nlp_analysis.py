from textblob import TextBlob
import re

def analyze_text(text):
    
    # -----------------------------
    # 1. Clean Text
    # -----------------------------
    clean_text = re.sub(r'[^\w\s]', '', text.lower())

    words = clean_text.split()
    word_count = len(words)

    # -----------------------------
    # 2. Sentiment Analysis
    # -----------------------------
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity      # -1 to +1
    subjectivity = blob.sentiment.subjectivity  # 0 to 1

    # -----------------------------
    # 3. Confidence Score
    # (Less subjectivity = more confident)
    # -----------------------------
    confidence = 1 - subjectivity

    # -----------------------------
    # 4. Filler Words Detection
    # -----------------------------
    filler_words = ["um", "uh", "like", "you know", "basically"]
    filler_count = sum(word in filler_words for word in words)

    # -----------------------------
    # 5. Keyword Matching (Basic AI)
    # -----------------------------
    important_keywords = ["project", "experience", "skill", "team", "development"]
    keyword_match = sum(word in important_keywords for word in words)

    # -----------------------------
    # 6. Sentence Length Quality
    # -----------------------------
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0

    # -----------------------------
    # 7. Return Features
    # -----------------------------
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "word_count": word_count,
        "filler_count": filler_count,
        "keyword_match": keyword_match,
        "avg_word_length": avg_word_length
    }