"""
Dual-mode matching engine.

Provides two matching strategies for comparing job descriptions against resumes:
- **Phase 1 (TF-IDF)**: Fast lexical matching using TF-IDF + cosine similarity.
- **Phase 2 (Semantic)**: Deep semantic matching using Sentence Transformers.
"""

import numpy as np
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Module-level cache for the sentence transformer model
_semantic_model = None


def tfidf_match(jd_text: str, resume_texts: list[str]) -> list[float]:
    """Phase 1: TF-IDF + Cosine Similarity matching.

    Parameters
    ----------
    jd_text : str
        Job description text.
    resume_texts : list[str]
        List of resume texts to compare against the JD.

    Returns
    -------
    list[float]
        Similarity scores (0–1) for each resume, in the same order as the
        input list.  Returns 0.0 for any resume that cannot be compared.
    """
    if not jd_text or not jd_text.strip():
        return [0.0] * len(resume_texts)

    if not resume_texts:
        return []

    # Filter out empty resume texts but track their positions
    valid_indices: list[int] = []
    valid_texts: list[str] = []
    for i, text in enumerate(resume_texts):
        if text and text.strip():
            valid_indices.append(i)
            valid_texts.append(text)

    if not valid_texts:
        return [0.0] * len(resume_texts)

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )

        # Fit on all documents together: JD first, then resumes
        all_docs = [jd_text] + valid_texts
        tfidf_matrix = vectorizer.fit_transform(all_docs)

        # Compute cosine similarity between the JD (row 0) and each resume
        jd_vector = tfidf_matrix[0:1]
        resume_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(jd_vector, resume_vectors).flatten()

        # Build full results array, filling in 0.0 for skipped resumes
        results = [0.0] * len(resume_texts)
        for idx, sim in zip(valid_indices, similarities):
            results[idx] = float(max(0.0, min(1.0, sim)))

        return results

    except Exception:
        return [0.0] * len(resume_texts)


def semantic_match(
    jd_text: str,
    resume_texts: list[str],
    model=None,
) -> list[float]:
    """Phase 2: Sentence Transformer semantic matching.

    Parameters
    ----------
    jd_text : str
        Job description text.
    resume_texts : list[str]
        List of resume texts.
    model : SentenceTransformer, optional
        Pre-loaded model.  If *None*, one will be loaded via
        :func:`get_semantic_model`.

    Returns
    -------
    list[float]
        Similarity scores (0–1) for each resume.
    """
    if not jd_text or not jd_text.strip():
        return [0.0] * len(resume_texts)

    if not resume_texts:
        return []

    if model is None:
        model = get_semantic_model()

    try:
        # Chunk long texts to stay within model's max token window (~512 tokens ≈ ~2000 chars)
        jd_chunks = _chunk_text(jd_text, max_chars=1500)
        jd_embeddings = model.encode(jd_chunks, show_progress_bar=False)
        # Average the JD chunk embeddings to get a single JD vector
        jd_embedding = np.mean(jd_embeddings, axis=0, keepdims=True)

        results: list[float] = []

        for resume_text in resume_texts:
            if not resume_text or not resume_text.strip():
                results.append(0.0)
                continue

            try:
                resume_chunks = _chunk_text(resume_text, max_chars=1500)
                resume_embeddings = model.encode(resume_chunks, show_progress_bar=False)

                # Compute similarity between JD embedding and each resume chunk,
                # then take the maximum score across chunks.
                sims = cosine_similarity(jd_embedding, resume_embeddings).flatten()
                best_sim = float(np.max(sims))
                results.append(max(0.0, min(1.0, best_sim)))
            except Exception:
                results.append(0.0)

        return results

    except Exception:
        return [0.0] * len(resume_texts)


def get_semantic_model():
    """Load and cache the sentence transformer model.

    Uses ``all-MiniLM-L6-v2`` — a lightweight, fast model with good quality.
    The model is cached at module level so it's only loaded once.

    Returns
    -------
    SentenceTransformer
    """
    global _semantic_model
    if _semantic_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for semantic matching. "
                "Install it with: pip install sentence-transformers"
            )
    return _semantic_model


def section_match(
    jd_sections: dict,
    resume_sections: dict,
    model=None,
) -> dict:
    """Compute section-level similarity scores.

    Compares corresponding sections (skills ↔ skills, experience ↔ experience)
    between the JD and the resume.

    Parameters
    ----------
    jd_sections : dict
        JD sections (keys like "skills", "experience", etc.).
    resume_sections : dict
        Resume sections (same key convention).
    model : SentenceTransformer, optional
        Pre-loaded model.

    Returns
    -------
    dict
        Section scores: ``{"skills": float, "experience": float, "overall": float}``
        All values are in [0, 1].
    """
    if model is None:
        model = get_semantic_model()

    section_scores: dict[str, float] = {}
    section_keys = ["skills", "experience"]

    for key in section_keys:
        jd_text = jd_sections.get(key, "")
        resume_text = resume_sections.get(key, "")

        if not jd_text or not resume_text:
            section_scores[key] = 0.0
            continue

        try:
            jd_emb = model.encode([jd_text], show_progress_bar=False)
            res_emb = model.encode([resume_text], show_progress_bar=False)
            sim = cosine_similarity(jd_emb, res_emb)[0][0]
            section_scores[key] = float(max(0.0, min(1.0, sim)))
        except Exception:
            section_scores[key] = 0.0

    # Overall: combine all available JD and resume text
    jd_full = " ".join(v for v in jd_sections.values() if isinstance(v, str) and v.strip())
    res_full = " ".join(v for v in resume_sections.values() if isinstance(v, str) and v.strip())

    if jd_full.strip() and res_full.strip():
        try:
            jd_emb = model.encode([jd_full], show_progress_bar=False)
            res_emb = model.encode([res_full], show_progress_bar=False)
            overall = cosine_similarity(jd_emb, res_emb)[0][0]
            section_scores["overall"] = float(max(0.0, min(1.0, overall)))
        except Exception:
            section_scores["overall"] = 0.0
    else:
        section_scores["overall"] = 0.0

    return section_scores


# ── Private helpers ──────────────────────────────────────────────────────

def _chunk_text(text: str, max_chars: int = 1500) -> list[str]:
    """Split text into chunks of approximately *max_chars* characters.

    Splits on paragraph boundaries (double newline) or sentence boundaries
    when paragraphs are too long.

    Always returns at least one chunk (the original text or a truncated
    version if splitting fails).
    """
    if not text or len(text) <= max_chars:
        return [text] if text else [""]

    # Try splitting on double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) + 1 > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            current_len = 0

        if len(para) > max_chars:
            # Split very long paragraphs on sentence boundaries
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            sentences = _split_sentences(para)
            sent_chunk: list[str] = []
            sent_len = 0
            for sent in sentences:
                if sent_len + len(sent) + 1 > max_chars and sent_chunk:
                    chunks.append(" ".join(sent_chunk))
                    sent_chunk = []
                    sent_len = 0
                sent_chunk.append(sent)
                sent_len += len(sent) + 1
            if sent_chunk:
                chunks.append(" ".join(sent_chunk))
        else:
            current_chunk.append(para)
            current_len += len(para) + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text[:max_chars]]


def _split_sentences(text: str) -> list[str]:
    """Naively split text into sentences."""
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]
