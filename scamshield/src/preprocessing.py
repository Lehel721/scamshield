"""Text preprocessing. normalize=True switches on the obfuscation defence."""
import re, unicodedata

ZW = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")
_H = {"\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c", "\u0445": "x", "\u0456": "i",
      "\u0455": "s", "\u0443": "y", "\u0410": "A", "\u0412": "B", "\u0415": "E", "\u041a": "K", "\u041c": "M",
      "\u041d": "H", "\u041e": "O", "\u0420": "P", "\u0421": "C", "\u0422": "T", "\u0425": "X"}
HOMO = str.maketrans(_H)
LEET = str.maketrans("013457@$", "oieastas")

SHORT = re.compile(r"\b(?:bit\.ly|tinyurl\.com|cutt\.ly|t\.co|goo\.gl|is\.gd|rb\.gy|shorturl\.at)/\S*", re.I)
URL = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+(?:\.[\w-]+)*\.(?:com|in|xyz|top|net|org|co|info|link|live|click|online|site)\b\S*", re.I)
PHONE = re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)")
MONEY = re.compile(r"(?:rs\.?|inr|\u20b9)\s?[\d,]+(?:\.\d+)?", re.I)
LONGNUM = re.compile(r"\d{5,}")
SPACED = re.compile(r"\b(?:[A-Za-z]\s){2,}[A-Za-z]\b")


def _leet_fix(m):
    tok = m.group(0)
    letters = sum(c.isalpha() for c in tok)
    if len(tok) >= 3 and letters >= 1 and letters / len(tok) >= 0.5 and any(c in "013457@$" for c in tok):
        return tok.translate(LEET)
    return tok


def normalize_text(t):
    t = unicodedata.normalize("NFKC", t)
    t = ZW.sub("", t).translate(HOMO)
    t = re.sub(r"hxxp", "http", t, flags=re.I)
    t = re.sub(r"\[\.\]|\(\.\)|\{\.\}", ".", t)
    t = SPACED.sub(lambda m: re.sub(r"\s", "", m.group(0)), t)
    t = re.sub(r"[A-Za-z0-9@$]+", _leet_fix, t)
    return t


def preprocess(text, normalize=False):
    t = str(text)
    if normalize:
        t = normalize_text(t)
    t = SHORT.sub(" shorturl ", t)
    t = URL.sub(" urltoken ", t)
    t = PHONE.sub(" phonetoken ", t)
    t = MONEY.sub(" moneytoken ", t)
    t = LONGNUM.sub(" longnumber ", t)
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()
