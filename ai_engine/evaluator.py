"""
RAGAS-Inspired Quantitative Evaluator (Member 2 — Phase 4)

Implements lightweight, zero-dependency evaluation metrics inspired by the
RAGAS framework (Shahul Es et al. 2023) for RAG pipeline quality assessment.

Since we cannot assume the real `ragas` library is installed (it requires
heavy dependencies including transformers and datasets), this module provides
self-contained, reproducible implementations:

  Faithfulness:
    Measures whether every factual claim in the generated response can be
    traced back to the retrieved context.  Approximated by computing what
    fraction of unique response content words appear in the context.
    Range: [0, 1] — 1.0 = fully grounded, 0.0 = completely hallucinated.

  Answer Relevance:
    Measures whether the response addresses the query/question topic.
    Approximated as the Jaccard similarity between query and response tokens.
    Range: [0, 1] — 1.0 = perfectly on-topic.

  Context Recall:
    Measures how much of the relevant information in the reference answer
    is covered by the retrieved context.
    Approximated by computing word overlap between context and reference.
    Range: [0, 1] — 1.0 = full coverage.

  Context Precision:
    Measures whether retrieved context chunks are relevant to the query.
    Approximated as the fraction of context words that appear in the response.
    Range: [0, 1] — 1.0 = all retrieved context was used.

These are approximations suitable for academic evaluation and reproducible
benchmarking without network access or LLM evaluation calls.

Usage:
    evaluator = RAGEvaluator()
    scores = evaluator.evaluate_response(
        query="Is palm oil healthy?",
        response="Palm oil is high in saturated fat which raises LDL cholesterol.",
        context="Palm oil contains 50% saturated fatty acids. High LDL is a risk factor.",
        reference="Palm oil is associated with elevated LDL cholesterol."
    )
    report = evaluator.evaluation_report(...)
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional


# ─────────────────────── Token utilities ─────────────────────────────────────

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "this", "that", "as", "from", "by", "not", "no", "so",
    "do", "does", "did", "has", "have", "had", "can", "will", "would",
    "should", "could", "may", "might", "shall", "very", "also", "when",
    "which", "who", "how", "if", "than", "then", "what", "all", "more",
}


def _tokenise(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Lowercase, strip punctuation, split on whitespace.
    Optionally removes common stopwords to focus on content words.
    """
    tokens = re.sub(r"[^\w\s]", "", text.lower()).split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    return tokens


def _token_set(text: str) -> set:
    return set(_tokenise(text))


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|."""
    if not a and not b:
        return 1.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def _overlap_recall(a: set, b: set) -> float:
    """Recall of set a relative to set b: |A ∩ B| / |A|."""
    if not a:
        return 1.0
    return len(a & b) / len(a)


# ─────────────────────────── RAGEvaluator class ───────────────────────────────

class RAGEvaluator:
    """
    Lightweight RAGAS-inspired evaluation suite for the FoodIntellect RAG pipeline.

    All metrics are computed locally using token-level overlap — no LLM calls,
    no network access, no external API keys required.  Results are reproducible
    and suitable for academic presentation.
    """

    # ── Core metric methods ───────────────────────────────────────────────────

    def faithfulness(self, response: str, context: str) -> float:
        """
        Estimate faithfulness: fraction of response content words grounded in context.

        A score of 1.0 means every content word in the response appears in the
        retrieved context (fully grounded, zero hallucination).
        A low score suggests the response contains information not backed by context.

        Args:
            response: LLM-generated response text.
            context:  Retrieved evidence context string.

        Returns:
            float in [0, 1].
        """
        resp_tokens = _token_set(response)
        ctx_tokens = _token_set(context)
        if not resp_tokens:
            return 1.0
        grounded = resp_tokens & ctx_tokens
        return round(len(grounded) / len(resp_tokens), 4)

    def answer_relevance(self, query: str, response: str) -> float:
        """
        Estimate answer relevance: Jaccard similarity between query and response tokens.

        Measures whether the response addresses the topic of the query.
        A score of 1.0 means query and response share all content words.

        Args:
            query:    Original user query or product name.
            response: LLM-generated response text.

        Returns:
            float in [0, 1].
        """
        q_tokens = _token_set(query)
        r_tokens = _token_set(response)
        return round(_jaccard(q_tokens, r_tokens), 4)

    def context_recall(self, reference: str, context: str) -> float:
        """
        Estimate context recall: coverage of reference answer by retrieved context.

        Measures how much of a gold-standard reference answer is contained within
        the retrieved context chunks.

        Args:
            reference: Gold-standard reference answer or product description.
            context:   Retrieved evidence context string.

        Returns:
            float in [0, 1].
        """
        ref_tokens = _token_set(reference)
        ctx_tokens = _token_set(context)
        return round(_overlap_recall(ref_tokens, ctx_tokens), 4)

    def context_precision(self, response: str, context: str) -> float:
        """
        Estimate context precision: fraction of context tokens used in the response.

        Measures whether all retrieved context was relevant (not just padded/noisy).

        Args:
            response: LLM-generated response text.
            context:  Retrieved evidence context string.

        Returns:
            float in [0, 1].
        """
        ctx_tokens = _token_set(context)
        resp_tokens = _token_set(response)
        if not ctx_tokens:
            return 1.0
        used = ctx_tokens & resp_tokens
        return round(len(used) / len(ctx_tokens), 4)

    # ── Combined evaluation ───────────────────────────────────────────────────

    def evaluate_response(
        self,
        query: str,
        response: str,
        context: str,
        reference: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Compute all four RAG evaluation metrics in one call.

        Args:
            query:     Original user query or product name.
            response:  LLM-generated response/summary text.
            context:   Retrieved evidence context (concatenated docs).
            reference: Optional gold-standard reference answer.
                       If None, the response itself is used as reference for
                       context_recall (measures context coverage of response).

        Returns:
            Dict with keys:
              - "faithfulness"       [0, 1]
              - "answer_relevance"   [0, 1]
              - "context_recall"     [0, 1]
              - "context_precision"  [0, 1]
              - "mean_score"         arithmetic mean of the four metrics
        """
        ref = reference if reference is not None else response

        scores = {
            "faithfulness":      self.faithfulness(response, context),
            "answer_relevance":  self.answer_relevance(query, response),
            "context_recall":    self.context_recall(ref, context),
            "context_precision": self.context_precision(response, context),
        }
        scores["mean_score"] = round(
            sum(scores[k] for k in ("faithfulness", "answer_relevance",
                                    "context_recall", "context_precision")) / 4.0,
            4,
        )
        return scores

    def evaluation_report(
        self,
        query: str,
        response: str,
        context: str,
        reference: Optional[str] = None,
    ) -> str:
        """
        Compute metrics and return a formatted human-readable report string.

        Args:
            query, response, context, reference: same as evaluate_response().

        Returns:
            Formatted multi-line report string suitable for console output
            or inclusion in academic documentation.
        """
        scores = self.evaluate_response(query, response, context, reference)

        lines = [
            "=" * 60,
            "  FoodIntellect RAG Pipeline — Evaluation Report (Member 2)",
            "=" * 60,
            f"  Query / Product    : {query[:60]}",
            "-" * 60,
            f"  Faithfulness       : {scores['faithfulness']:.4f}  "
            f"({'✓ grounded' if scores['faithfulness'] >= 0.7 else '⚠ hallucination risk'})",
            f"  Answer Relevance   : {scores['answer_relevance']:.4f}  "
            f"({'✓ on-topic' if scores['answer_relevance'] >= 0.2 else '⚠ off-topic'})",
            f"  Context Recall     : {scores['context_recall']:.4f}  "
            f"({'✓ good coverage' if scores['context_recall'] >= 0.4 else '⚠ poor coverage'})",
            f"  Context Precision  : {scores['context_precision']:.4f}  "
            f"({'✓ precise' if scores['context_precision'] >= 0.2 else '⚠ noisy context'})",
            "-" * 60,
            f"  Mean Score         : {scores['mean_score']:.4f}",
            "=" * 60,
        ]
        return "\n".join(lines)

    def batch_evaluate(
        self,
        samples: List[Dict],
    ) -> Dict:
        """
        Evaluate a batch of RAG samples and return aggregate statistics.

        Each sample dict should contain:
          - "query"     (str, required)
          - "response"  (str, required)
          - "context"   (str, required)
          - "reference" (str, optional)

        Returns:
            Dict with "per_sample" list and "aggregate" summary (mean of each metric).
        """
        per_sample = []
        for s in samples:
            scores = self.evaluate_response(
                query=s.get("query", ""),
                response=s.get("response", ""),
                context=s.get("context", ""),
                reference=s.get("reference"),
            )
            per_sample.append({**s, "scores": scores})

        if not per_sample:
            return {"per_sample": [], "aggregate": {}}

        metric_keys = ("faithfulness", "answer_relevance", "context_recall",
                       "context_precision", "mean_score")
        aggregate = {
            k: round(sum(r["scores"][k] for r in per_sample) / len(per_sample), 4)
            for k in metric_keys
        }
        return {"per_sample": per_sample, "aggregate": aggregate}
