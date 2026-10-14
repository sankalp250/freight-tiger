import os
import csv
import math
import hashlib
from typing import List, Dict, Any
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

class DeterministicTextEmbedding(EmbeddingFunction):
    """
    Fast, 100% offline, deterministic embedding function for ChromaDB.
    Generates a 128-dimensional dense vector using token hashing and n-gram term frequency
    with L2 normalization. Guarantees 0 external network requests and 100% reproducibility.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def name(self) -> str:
        return "deterministic_text_embedding"

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = text.lower().replace("-", " ").split()
        if not tokens:
            return vec

        # Unigrams and bigrams
        terms = list(tokens)
        for i in range(len(tokens) - 1):
            terms.append(f"{tokens[i]}_{tokens[i+1]}")

        for term in terms:
            # Deterministic bucket hash
            h = int(hashlib.sha256(term.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed_single(doc) for doc in input]


class NotesKnowledgeStore:
    """
    Manages vector embeddings and metadata indexing for context_notes.csv in ChromaDB.
    Persists locally in ./data/chroma_db for 100% offline, zero-cloud-dependency execution.
    """
    def __init__(self, persist_dir: str = None, collection_name: str = "freight_context_notes"):
        if persist_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            persist_dir = os.path.join(base_dir, "data", "chroma_db")

        os.makedirs(persist_dir, exist_ok=True)
        self.embedding_fn = DeterministicTextEmbedding(dim=128)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "FreightTiger Route Context Notes & Disruptions"}
        )

    def populate_from_csv(self, csv_path: str) -> int:
        """Reads context_notes.csv and stores them in ChromaDB with metadata."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Notes file not found: {csv_path}")

        notes = []
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes.append({
                    "note_id": row["note_id"].strip(),
                    "date": row["date"].strip(),
                    "applies_to": row["applies_to"].strip(),
                    "note": row["note"].strip(),
                })

        # Upsert into ChromaDB
        ids = [n["note_id"] for n in notes]
        documents = [
            f"Note {n['note_id']} on {n['date']} for {n['applies_to']}: {n['note']}"
            for n in notes
        ]
        metadatas = [
            {
                "note_id": n["note_id"],
                "date": n["date"],
                "applies_to": n["applies_to"],
                "raw_text": n["note"]
            }
            for n in notes
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return len(notes)

    def search_similar_notes(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Performs vector similarity search over context notes."""
        count = self.collection.count()
        if count == 0:
            return []

        res = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        results = []
        if res and res["metadatas"] and len(res["metadatas"]) > 0:
            for i, meta in enumerate(res["metadatas"][0]):
                results.append({
                    "note_id": meta["note_id"],
                    "date": meta["date"],
                    "applies_to": meta["applies_to"],
                    "note": meta["raw_text"],
                    "distance": res["distances"][0][i] if "distances" in res and res["distances"] else 0.0
                })
        return results

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Retrieves all indexed notes directly."""
        data = self.collection.get()
        notes = []
        if data and data["metadatas"]:
            for meta in data["metadatas"]:
                notes.append({
                    "note_id": meta["note_id"],
                    "date": meta["date"],
                    "applies_to": meta["applies_to"],
                    "note": meta["raw_text"],
                })
        notes.sort(key=lambda x: x["note_id"])
        return notes
