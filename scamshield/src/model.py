"""ScamShield classifier: word + character TF-IDF -> Logistic Regression."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from src.preprocessing import preprocess


class ScamModel:
    def __init__(self, normalize=False, C=10.0, name="model"):
        self.normalize, self.name = normalize, name
        self.vec = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=30000, sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, max_features=60000, sublinear_tf=True)),
        ])
        self.clf = LogisticRegression(C=C, max_iter=3000, class_weight="balanced")

    def _prep(self, texts):
        return [preprocess(t, self.normalize) for t in texts]

    def fit(self, texts, y):
        self.clf.fit(self.vec.fit_transform(self._prep(texts)), y)
        return self

    def predict_proba(self, texts):
        return self.clf.predict_proba(self.vec.transform(self._prep(list(texts))))[:, 1]

    def predict(self, texts, thr=0.5):
        return (self.predict_proba(texts) >= thr).astype(int)
