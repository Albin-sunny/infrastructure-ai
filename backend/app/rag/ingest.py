from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

import faiss
import numpy as np
import pickle
import os


# ==========================
# Load PDFs
# ==========================

text = ""

pdf_folder = "data/manuals"

for file in os.listdir(pdf_folder):

    if file.endswith(".pdf"):

        reader = PdfReader(
            os.path.join(pdf_folder, file)
        )

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"


# ==========================
# Chunking
# ==========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_text(text)

print("Chunks:", len(chunks))


# ==========================
# Embeddings
# ==========================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = model.encode(
    chunks,
    normalize_embeddings=True
)

embeddings = np.array(
    embeddings,
    dtype="float32"
)


# ==========================
# FAISS Index
# ==========================

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(
    dimension
)

index.add(embeddings)

faiss.write_index(
    index,
    "faiss_index.bin"
)


# ==========================
# Save Chunks
# ==========================

with open("chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)


# ==========================
# TF-IDF
# ==========================

vectorizer = TfidfVectorizer(
    stop_words="english"
)

tfidf_matrix = vectorizer.fit_transform(
    chunks
)

with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("tfidf_matrix.pkl", "wb") as f:
    pickle.dump(tfidf_matrix, f)


print("FAISS index saved")
print("TF-IDF saved")
print("Vector database build complete")