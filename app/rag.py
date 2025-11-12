from typing import List, Tuple
import os, glob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SimpleRAG:
    def __init__(self, data_dir: str, embedding_model: str):
        self.data_dir = data_dir
        self.model = SentenceTransformer(embedding_model)
        self.texts: List[str] = []
        self.index = None
        self._build()

    def _load_texts(self) -> List[str]:
        paths = glob.glob(os.path.join(self.data_dir, "*.txt")) + glob.glob(os.path.join(self.data_dir, "*.md"))
        texts = []
        for p in paths:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                texts.append(f.read())
        return texts

    def _build(self):
        self.texts = self._load_texts()
        if not self.texts:
            self.index = None
            return
        embeddings = self.model.encode(self.texts, convert_to_numpy=True, normalize_embeddings=True)
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(d)
        self.index.add(embeddings)

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        if self.index is None or not self.texts:
            return []
        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = self.index.search(q, k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            results.append((self.texts[int(idx)], float(score)))
        return results
