"""
OCR Accuracy Evaluator (Member 1 -- Phase 4 Academic Evaluation)

Measures Character Error Rate (CER) and Word Error Rate (WER) for OCR
provider outputs against ground-truth ingredient text strings.

These metrics are standard academic benchmarks for OCR system evaluation:

  CER = edit_distance(reference, hypothesis) / len(reference)
        at the character level (Levenshtein distance).

  WER = edit_distance(ref_words, hyp_words) / len(ref_words)
        at the word level (whitespace-tokenised).

Both CER and WER are in [0, infinity) -- lower is better.
A CER/WER of 0.0 means the OCR output exactly matches the ground truth.

Usage:
    evaluator = OCREvaluator()

    # Single sample
    cer = evaluator.compute_cer("Whole Wheat Flour", "Whole Wh0at Flour")
    wer = evaluator.compute_wer("Whole Wheat Flour", "Whole Wh0at Flour")

    # Batch evaluation
    results = evaluator.evaluate_dataset([
        {"reference": "Sugar, Palm Oil", "hypothesis": "Sugar, Palm 0il",
         "provider": "easyocr", "image_id": "label_001"},
    ])
    summary = evaluator.compute_summary(results)

References:
  - Levenshtein (1966), Morris et al. (2004)
"""

from typing import List, Dict
import re


class OCREvaluator:
    """
    Computes CER and WER for OCR provider benchmarking.
    No external dependencies -- pure Python standard library only.
    """

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def compute_cer(self, reference: str, hypothesis: str) -> float:
        """
        Character Error Rate: edit_distance(ref, hyp) / len(ref).

        Args:
            reference:  Ground truth text string.
            hypothesis: OCR output text string.

        Returns:
            CER float in [0, inf). 0.0 = perfect match.
        """
        if not reference:
            return 0.0
        return self._edit_distance(reference, hypothesis) / len(reference)

    def compute_wer(self, reference: str, hypothesis: str) -> float:
        """
        Word Error Rate: edit_distance(ref_tokens, hyp_tokens) / len(ref_tokens).

        Words are obtained by lower-casing and whitespace-splitting after
        stripping punctuation so "Flour," == "Flour" at the word level.

        Args:
            reference:  Ground truth text string.
            hypothesis: OCR output text string.

        Returns:
            WER float in [0, inf). 0.0 = perfect match.
        """
        ref_words = self._tokenise(reference)
        hyp_words = self._tokenise(hypothesis)
        if not ref_words:
            return 0.0
        return self._edit_distance(ref_words, hyp_words) / len(ref_words)

    def evaluate_dataset(self, samples: List[Dict]) -> List[Dict]:
        """
        Evaluate a list of OCR samples and return per-sample metrics.

        Each sample dict may contain:
          - "reference"  (str, required): Ground truth text.
          - "hypothesis" (str, required): OCR output text.
          - "provider"   (str, optional): e.g. "easyocr", "tesseract", "mock".
          - "image_id"   (str, optional): Image filename or identifier.

        Returns a list of result dicts, each with:
          - All input keys preserved.
          - "cer":         Computed CER (4 dp).
          - "wer":         Computed WER (4 dp).
          - "exact_match": True if hypothesis == reference (case-insensitive).
        """
        results = []
        for sample in samples:
            ref = sample.get("reference", "")
            hyp = sample.get("hypothesis", "")
            cer = self.compute_cer(ref, hyp)
            wer = self.compute_wer(ref, hyp)
            results.append({
                "image_id": sample.get("image_id", ""),
                "provider": sample.get("provider", "unknown"),
                "reference": ref,
                "hypothesis": hyp,
                "cer": round(cer, 4),
                "wer": round(wer, 4),
                "exact_match": ref.strip().lower() == hyp.strip().lower(),
            })
        return results

    def compute_summary(
        self,
        results: List[Dict],
        group_by_provider: bool = True,
    ) -> Dict:
        """
        Aggregate statistics from evaluate_dataset() output.

        Returns:
            {
              "overall": {"mean_cer", "mean_wer", "exact_match_rate", "n_samples"},
              "by_provider": {
                  "easyocr":   {"mean_cer", "mean_wer", "exact_match_rate", "n_samples"},
                  "tesseract": {...},
              }
            }
        """
        if not results:
            return {"overall": {"mean_cer": 0.0, "mean_wer": 0.0,
                                "exact_match_rate": 0.0, "n_samples": 0}}

        summary: Dict = {"overall": self._aggregate_metrics(results)}

        if group_by_provider:
            providers: Dict[str, List[Dict]] = {}
            for r in results:
                p = r.get("provider", "unknown")
                providers.setdefault(p, []).append(r)
            summary["by_provider"] = {
                p: self._aggregate_metrics(grp)
                for p, grp in providers.items()
            }

        return summary

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tokenise(text: str) -> List[str]:
        """Lowercase + strip punctuation + whitespace-split for WER."""
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        return cleaned.split()

    @staticmethod
    def _edit_distance(a, b) -> int:
        """
        Standard dynamic-programming Levenshtein distance.
        Works on any sequence (str for CER, list of tokens for WER).
        """
        la, lb = len(a), len(b)
        dp = [[0] * (lb + 1) for _ in range(la + 1)]
        for i in range(la + 1):
            dp[i][0] = i
        for j in range(lb + 1):
            dp[0][j] = j
        for i in range(1, la + 1):
            for j in range(1, lb + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[la][lb]

    @staticmethod
    def _aggregate_metrics(results: List[Dict]) -> Dict:
        """Compute mean CER, mean WER, and exact-match rate."""
        n = len(results)
        if n == 0:
            return {"mean_cer": 0.0, "mean_wer": 0.0,
                    "exact_match_rate": 0.0, "n_samples": 0}
        return {
            "mean_cer": round(sum(r["cer"] for r in results) / n, 4),
            "mean_wer": round(sum(r["wer"] for r in results) / n, 4),
            "exact_match_rate": round(sum(1 for r in results if r["exact_match"]) / n, 4),
            "n_samples": n,
        }
