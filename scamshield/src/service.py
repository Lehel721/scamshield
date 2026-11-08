"""Framework-free analysis service shared by the Vercel API and any other front end.

Mirrors the logic of the Streamlit demo (app.py) without depending on Streamlit or pandas.
"""
import csv
import json
import random
from functools import lru_cache

import joblib

import config
from src.explain import explain
from src.rag import Retriever
from src.robustness import ATTACKS

MAX_CHARS = 2000


@lru_cache(maxsize=1)
def load_models():
    model = joblib.load(config.MODEL_DIR / "scamshield.joblib")
    baseline = joblib.load(config.MODEL_DIR / "baseline.joblib")
    retriever = Retriever(config.KB_PATH)
    return model, baseline, retriever


def analyse(message, attack="None"):
    message = str(message or "")[:MAX_CHARS]
    if not message.strip():
        raise ValueError("Paste an SMS message before analysing it.")
    if attack not in ("None", "", None) and attack not in ATTACKS:
        raise ValueError(f"Unknown obfuscation test: {attack}")

    model, baseline, retriever = load_models()
    analysed_text = message
    if attack and attack != "None":
        analysed_text = ATTACKS[attack](message, random.Random(3))

    result = explain(analysed_text, model, retriever)
    baseline_probability = float(baseline.predict_proba([analysed_text])[0])

    if result["is_scam"]:
        verdict_class, verdict_label = "scam", "SCAM DETECTED"
    elif len(result.get("red_flags", [])) >= 3:
        verdict_class, verdict_label = "caution", "USE CAUTION"
    else:
        verdict_class, verdict_label = "safe", "LIKELY LEGITIMATE"

    return {
        "analysed_text": analysed_text,
        "attack_name": attack or "None",
        "verdict_class": verdict_class,
        "verdict_label": verdict_label,
        "headline": result["headline"],
        "why": result["why"],
        "scam_probability": float(result["scam_probability"]),
        "baseline_probability": baseline_probability,
        "red_flags": result["red_flags"],
        "advice": list(result["advice"]),
        "sources": [{"title": t, "similarity": s} for t, s in result["sources"]],
    }


def _read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metrics():
    retrieval_path = config.RESULTS_DIR / "retrieval.json"
    return {
        "attacks": list(ATTACKS),
        "metrics": _read_csv(config.RESULTS_DIR / "metrics.csv"),
        "robustness": _read_csv(config.RESULTS_DIR / "robustness.csv"),
        "retrieval": json.loads(retrieval_path.read_text()) if retrieval_path.exists() else None,
    }
