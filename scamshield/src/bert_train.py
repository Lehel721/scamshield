"""OPTIONAL: fine-tune DistilBERT on the same data and compare with the classical model.
Needs: pip install torch transformers. Runs on CPU (slow) or free Colab GPU.
Usage: python src/bert_train.py --epochs 1 --max-classic 2000
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd, torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import config
from src.train import load_classic
from src.evaluate import metrics
from src.robustness import ATTACKS, attack_texts

ap = argparse.ArgumentParser()
ap.add_argument("--epochs", type=int, default=1); ap.add_argument("--max-classic", type=int, default=2000)
ap.add_argument("--batch", type=int, default=16); ap.add_argument("--maxlen", type=int, default=64)
a = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"

classic = load_classic()
ctr, cte = train_test_split(classic, test_size=config.TEST_SIZE, stratify=classic.label, random_state=config.SEED)
ctr = ctr.sample(min(a.max_classic, len(ctr)), random_state=1)
itr, ite = pd.read_csv(config.INDIAN_TRAIN), pd.read_csv(config.INDIAN_TEST)
train = pd.concat([ctr, itr[["text", "label"]]]).sample(frac=1, random_state=1)

tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2).to(dev)

def enc(texts):
    e = tok(list(texts), truncation=True, padding="max_length", max_length=a.maxlen, return_tensors="pt")
    return e["input_ids"], e["attention_mask"]

ids, mask = enc(train.text)
dl = DataLoader(TensorDataset(ids, mask, torch.tensor(train.label.values)), batch_size=a.batch, shuffle=True)
opt = torch.optim.AdamW(model.parameters(), lr=3e-5)
for ep in range(a.epochs):
    model.train()
    for i, (x, m, y) in enumerate(dl):
        loss = model(input_ids=x.to(dev), attention_mask=m.to(dev), labels=y.to(dev)).loss
        loss.backward(); opt.step(); opt.zero_grad()
        if i % 50 == 0: print(f"epoch {ep+1} step {i}/{len(dl)} loss {loss.item():.3f}")

@torch.no_grad()
def predict(texts):
    model.eval(); out = []
    x, m = enc(texts)
    for i in range(0, len(texts), 64):
        out += model(input_ids=x[i:i+64].to(dev), attention_mask=m[i:i+64].to(dev)).logits.argmax(-1).cpu().tolist()
    return out

rows = []
for name, d in {"Classic SMS test": cte, "Indian test (hand-written)": ite}.items():
    rows.append(dict(model="DistilBERT", test_set=name, **metrics(d.label, predict(d.text.tolist()))))
scams = ite[ite.label == 1].text.tolist()
rob = [dict(model="DistilBERT", attack="clean", recall=sum(predict(scams)) / len(scams))]
for atk in ATTACKS:
    rob.append(dict(model="DistilBERT", attack=atk, recall=sum(predict(attack_texts(scams, atk, 0))) / len(scams)))
pd.DataFrame(rows).to_csv(config.RESULTS_DIR / "bert_metrics.csv", index=False)
pd.DataFrame(rob).to_csv(config.RESULTS_DIR / "bert_robustness.csv", index=False)
print(pd.DataFrame(rows).round(3)); print(pd.DataFrame(rob).round(3))
