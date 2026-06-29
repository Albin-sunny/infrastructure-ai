from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import faiss
import pickle
import numpy as np


# ==========================
# Load Model
# ==========================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================
# Load FAISS
# ==========================

index = faiss.read_index(
    "faiss_index.bin"
)


# ==========================
# Load Chunks
# ==========================

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)


# ==========================
# Load TF-IDF
# ==========================

with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("tfidf_matrix.pkl", "rb") as f:
    tfidf_matrix = pickle.load(f)


# ==========================
# Hybrid Retrieval
# ==========================

def retrieve(query, k=5):

    try:

        # ------------------
        # Semantic Search
        # ------------------

        query_embedding = model.encode(
            [query],
            normalize_embeddings=True
        ).astype("float32")

        semantic_scores, semantic_indices = index.search(
            query_embedding,
            20
        )

        # ------------------
        # TF-IDF Search
        # ------------------

        query_tfidf = vectorizer.transform(
            [query]
        )

        keyword_scores = cosine_similarity(
            query_tfidf,
            tfidf_matrix
        ).flatten()

        keyword_top_indices = np.argsort(
            keyword_scores
        )[::-1][:20]

        candidate_indices = set(
            semantic_indices[0]
        )

        candidate_indices.update(
            keyword_top_indices
    )

        # ------------------
        # Hybrid Scoring
        # ------------------

        scored_chunks = []

        for idx in candidate_indices:

            if idx >= len(chunks):
                continue

            semantic_score = 0.0

            if idx in semantic_indices[0]:

                semantic_position = list(
                    semantic_indices[0]
                ).index(idx)

                semantic_score = float(
                    semantic_scores[0][semantic_position]
                )

            keyword_score = float(
                keyword_scores[idx]
            )

            final_score = (
                0.8 * semantic_score
                +
                0.2 * keyword_score
            )

            scored_chunks.append(
                (
                final_score,
                chunks[idx]
                )
        )

        # ------------------
        # Sort Results
        # ------------------

        scored_chunks.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        results = []

        for score, chunk in scored_chunks[:k]:

            if score < 0.40:
                continue

            results.append(chunk)

        return results

    except Exception as e:

        print(
            "Retriever Error:",
            str(e)
        )

        return []