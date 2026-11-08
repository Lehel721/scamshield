"""Retrieval over the scam knowledge base (TF-IDF cosine similarity)."""
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from src.preprocessing import preprocess


class Retriever:
    def __init__(self, kb_path):
        self.docs = json.load(open(kb_path, encoding="utf-8"))
        corpus = [f"{d['title']} {d['summary']} {d['keywords']} {' '.join(d['red_flags'])}" for d in self.docs]
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        self.mat = self.vec.fit_transform([preprocess(c, True) for c in corpus])

    def search(self, query, k=3):
        q = self.vec.transform([preprocess(query, True)])
        sims = linear_kernel(q, self.mat).ravel()
        order = sims.argsort()[::-1][:k]
        return [(self.docs[i], float(sims[i])) for i in order]
