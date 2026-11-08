"""Obfuscation attacks used by real smishers to dodge filters."""
import random

LEET_A = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$"}
HOMO_A = {"a": "\u0430", "e": "\u0435", "o": "\u043e", "p": "\u0440", "c": "\u0441", "x": "\u0445",
          "A": "\u0410", "E": "\u0415", "O": "\u041e", "P": "\u0420", "C": "\u0421", "X": "\u0425"}


def leetspeak(t, rng, p=0.6):
    return "".join(LEET_A[c.lower()] if c.lower() in LEET_A and rng.random() < p else c for c in t)


def homoglyph(t, rng, p=0.6):
    return "".join(HOMO_A[c] if c in HOMO_A and rng.random() < p else c for c in t)


def zero_width(t, rng, p=0.3):
    out = []
    for i, c in enumerate(t):
        out.append(c)
        if c.isalpha() and i + 1 < len(t) and t[i + 1].isalpha() and rng.random() < p:
            out.append("\u200b")
    return "".join(out)


def spacing(t, rng, p=0.5):
    words = []
    for w in t.split(" "):
        if w.isalpha() and len(w) >= 3 and rng.random() < p:
            w = " ".join(w)
        words.append(w)
    return " ".join(words)


def url_obfuscation(t, rng, p=1.0):
    t = t.replace("http", "hxxp")
    out = []
    for tok in t.split(" "):
        if any(k in tok for k in ("bit.ly", "tinyurl", "cutt.ly", "hxxp", ".xyz", ".top", ".live", ".site", ".click", ".net", ".in/")):
            tok = tok.replace(".", "[.]")
        out.append(tok)
    return " ".join(out)


def combined(t, rng):
    return url_obfuscation(zero_width(leetspeak(t, rng, 0.4), rng, 0.2), rng)


ATTACKS = {"leetspeak": leetspeak, "homoglyph": homoglyph, "zero_width": zero_width,
           "spacing": spacing, "url_obfuscation": url_obfuscation, "combined": combined}


def attack_texts(texts, name, seed=0):
    rng = random.Random(seed)
    return [ATTACKS[name](t, rng) for t in texts]


def random_attack(text, rng):
    name = rng.choice(list(ATTACKS))
    return ATTACKS[name](text, rng)
