"""Verdict + red flags + retrieved advice -> a user-friendly explanation."""
from src.redflags import find_red_flags


def explain(message, model, retriever, threshold=0.5, k=3):
    p = float(model.predict_proba([message])[0])
    flags = find_red_flags(message)
    hits = retriever.search(message, k=k)
    top, score = hits[0]
    is_scam = p >= threshold
    if is_scam and score >= 0.08 and top["type"] != "general":
        scam_type, doc = top["title"], top
    elif is_scam:
        scam_type, doc = "Suspicious message (type unclear)", next(d for d, _ in hits if d["type"] == "general") if any(d["type"] == "general" for d, _ in hits) else top
    else:
        scam_type, doc = None, None

    if is_scam:
        headline = f"Likely SCAM - {scam_type}"
        why = doc["summary"]
        advice = doc["what_to_do"]
    elif len(flags) >= 3:
        headline = "Looks legitimate to the model, but has several red flags - be careful"
        why = "The classifier is not confident this is a scam, yet multiple warning signs were found."
        advice = ["Do not click links or share OTP / PIN", "Verify using the official app or website"]
    else:
        headline = "Likely legitimate"
        why = "No strong scam pattern found."
        advice = ["Still: never share OTP, PIN or CVV with anyone."]
    return {"is_scam": is_scam, "scam_probability": p, "headline": headline, "why": why,
            "red_flags": flags, "advice": advice, "sources": [(d["title"], round(s, 3)) for d, s in hits]}
