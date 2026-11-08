import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def metrics(y, pred):
    return dict(accuracy=accuracy_score(y, pred), precision=precision_score(y, pred, zero_division=0),
                recall=recall_score(y, pred, zero_division=0), f1=f1_score(y, pred, zero_division=0))


def plot_f1(df, out):
    p = df.pivot(index="model", columns="test_set", values="f1")
    p = p.loc[df["model"].drop_duplicates()]
    p.plot(kind="bar", figsize=(9, 5)); plt.ylim(0, 1.05); plt.ylabel("F1"); plt.xticks(rotation=20, ha="right")
    plt.title("F1 on clean test sets"); plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()


def plot_robust(df, out):
    import seaborn as sns
    p = df.pivot(index="model", columns="attack", values="recall")
    p = p.loc[df["model"].drop_duplicates()]
    plt.figure(figsize=(9, 4)); sns.heatmap(p, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1)
    plt.title("Scam recall under obfuscation attacks (Indian test set)"); plt.tight_layout()
    plt.savefig(out, dpi=150); plt.close()
