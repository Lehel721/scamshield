"""Rule-based red-flag finder: makes the verdict explainable."""
import re

RULES = [
 ("Urgency / deadline", r"\b(urgent|immediately|today|tonight|within \d+\s*(hours?|hrs?|minutes?|mins?)|expir\w*|last (warning|chance)|final notice|turant|aaj (hi|raat))\b",
  "Scammers rush you so you do not stop to think."),
 ("Threat of blocking / disconnection", r"\b(block(ed)?|suspend(ed)?|disconnect(ed)?|deactivat\w*|freeze|terminat\w*|band ho|kat jayega|lapse)\b",
  "Real banks and utilities do not threaten you over SMS."),
 ("Link in the message", r"(https?://|www\.|hxxp)|\b[\w-]+\.(com|in|xyz|top|net|live|click|site)\b",
  "Links in unexpected SMS often lead to fake login pages."),
 ("Shortened link", r"\b(bit\.ly|tinyurl|cutt\.ly|t\.co|goo\.gl|is\.gd|rb\.gy)\b|bit\[\.\]ly",
  "Short links hide the real destination."),
 ("Suspicious domain ending", r"\.(xyz|top|live|click|site)\b|\.in\.net|\.net/",
  "Look-alike domains imitate real brands."),
 ("Prize / refund / cashback bait", r"\b(won|winner|prize|lottery|lucky draw|cashback|refund|reward points?|giveaway|jeeta|inaam)\b",
  "Unexpected money is the classic bait."),
 ("Asks you to share OTP / PIN / CVV", r"(?<!not )(?<!never )(?<!n't )\b(share|send|enter|provide|reply with|approve)\b.{0,30}\b(otp|pin|cvv|password|collect request)\b|\bsend\b.{0,20}aadhaar",
  "Nobody legitimate will ask for your OTP, PIN or CVV."),
 ("Fee demanded upfront", r"\b(registration fee|processing fee|insurance charge|delivery charge|clearance charge|redelivery fee|deposit)\b|\bpay rs\.? ?[\d,]+",
  "Genuine jobs, loans and prizes never need an advance fee."),
 ("Asks you to call a mobile number", r"\b(call|contact|whatsapp|dial)\b.{0,40}\b[6-9]\d{9}\b|\bpress 9\b",
  "Scammers want a live conversation to pressure you."),
 ("Impersonates an authority", r"\b(rbi|trai|income tax|customs|police|uidai|india post|kbc)\b",
  "Official names are borrowed to look trustworthy."),
 ("Unusual obfuscation (symbols / hidden characters)", r"[\u200b\u200c\u200d\u0400-\u04ff]|\[\.\]|\b\w*[a-z][@$30]\w*[a-z]\w*\b",
  "Odd characters are used to slip past spam filters."),
]
_C = [(n, re.compile(p, re.I), why) for n, p, why in RULES]


def find_red_flags(text):
    return [{"flag": n, "why": why} for n, rx, why in _C if rx.search(text)]
