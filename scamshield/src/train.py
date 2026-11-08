"""Train + compare models, run robustness suite, evaluate retrieval, save models."""
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import joblib, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split

import config
from src.model import ScamModel
from src.robustness import ATTACKS, attack_texts, random_attack
from src.evaluate import metrics, plot_f1, plot_robust
from src.rag import Retriever


def load_classic():
    df = pd.read_csv(config.CLASSIC_PATH, encoding="latin-1").rename(columns={"v1": "label", "v2": "text"})[["label", "text"]]
    df = df.dropna().drop_duplicates().reset_index(drop=True)
    df["label"] = df["label"].map({"ham": 0, "spam": 1})
    return df


def augment(texts, labels, seed=0):
    """Adversarial augmentation: add attacked copies of all scams and 30% of legit messages."""
    rng = random.Random(seed)
    t2, y2 = list(texts), list(labels)
    for t, y in zip(texts, labels):
        if y == 1 or rng.random() < 0.3:
            t2.append(random_attack(t, rng)); y2.append(y)
    return t2, y2


def main():
    config.RESULTS_DIR.mkdir(exist_ok=True); config.MODEL_DIR.mkdir(exist_ok=True)
    classic = load_classic()
    ctr, cte = train_test_split(classic, test_size=config.TEST_SIZE, stratify=classic.label, random_state=config.SEED)
    itr, ite = pd.read_csv(config.INDIAN_TRAIN), pd.read_csv(config.INDIAN_TEST)
    print(f"classic train/test: {len(ctr)}/{len(cte)} | indian train/test: {len(itr)}/{len(ite)}")

    X_base, y_base = ctr.text.tolist(), ctr.label.tolist()
    X_all = X_base + itr.text.tolist(); y_all = y_base + itr.label.tolist()
    X_adv, y_adv = augment(X_all, y_all, config.SEED)

    specs = [("A. Baseline (classic data only)", False, X_base, y_base),
             ("B. + Indian data", False, X_all, y_all),
             ("C. + Normalization", True, X_all, y_all),
             ("D. + Adversarial training", False, X_adv, y_adv),
             ("E. ScamShield (Norm + Adv. training)", True, X_adv, y_adv)]
    models = {}
    for name, norm, X, y in specs:
        print("training", name); models[name] = ScamModel(normalize=norm, name=name).fit(X, y)

    rows = []
    sets = {"Classic SMS test": cte, "Indian test (hand-written)": ite, "Indian Hinglish subset": ite[ite.hinglish == 1]}
    for name, m in models.items():
        for sname, d in sets.items():
            rows.append(dict(model=name, test_set=sname, **metrics(d.label, m.predict(d.text))))
    res = pd.DataFrame(rows); res.to_csv(config.RESULTS_DIR / "metrics.csv", index=False)
    plot_f1(res, config.RESULTS_DIR / "f1_comparison.png")

    rob = []
    scams, hams = ite[ite.label == 1].text.tolist(), ite[ite.label == 0].text.tolist()
    for name, m in models.items():
        rob.append(dict(model=name, attack="clean", recall=float(m.predict(scams).mean()), fpr=float(m.predict(hams).mean())))
        for atk in ATTACKS:
            rec, fpr = [], []
            for s in range(config.ATTACK_SEEDS):
                rec.append(m.predict(attack_texts(scams, atk, s)).mean()); fpr.append(m.predict(attack_texts(hams, atk, s)).mean())
            rob.append(dict(model=name, attack=atk, recall=float(np.mean(rec)), fpr=float(np.mean(fpr))))
    rob = pd.DataFrame(rob); rob.to_csv(config.RESULTS_DIR / "robustness.csv", index=False)
    plot_robust(rob, config.RESULTS_DIR / "robustness_heatmap.png")

    ret = Retriever(config.KB_PATH); sc = ite[ite.label == 1]
    h1 = h3 = 0
    for t, ty in zip(sc.text, sc.scam_type):
        types = [d["type"] for d, _ in ret.search(t, k=3)]
        h1 += types[0] == ty; h3 += ty in types
    rag = dict(hit_at_1=h1 / len(sc), hit_at_3=h3 / len(sc), n=len(sc))
    pd.Series(rag).to_json(config.RESULTS_DIR / "retrieval.json")

    pd.set_option("display.width", 200)
    print("\n=== Clean test results (F1) ===\n", res.pivot(index="model", columns="test_set", values="f1").round(3).to_string())
    print("\n=== Scam recall under attack ===\n", rob.pivot(index="model", columns="attack", values="recall").round(2).to_string())
    print("\n=== False-positive rate under attack ===\n", rob.pivot(index="model", columns="attack", values="fpr").round(2).to_string())
    print("\n=== Retrieval ===", rag)
    joblib.dump(models["A. Baseline (classic data only)"], config.MODEL_DIR / "baseline.joblib")
    joblib.dump(models["E. ScamShield (Norm + Adv. training)"], config.MODEL_DIR / "scamshield.joblib")
    print("\nSaved models/baseline.joblib and models/scamshield.joblib")


if __name__ == "__main__":
    main()
