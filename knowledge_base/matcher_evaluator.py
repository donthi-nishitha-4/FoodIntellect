"""
Ingredient Normalization Evaluator (Member 1 -- Phase 4 Academic Evaluation)

Measures precision, recall, and F1-score for the IngredientMatcher module
by comparing its match decisions against a labelled ground-truth dataset.

Metric definitions (standard IR binary classification):
  - True Positive  (TP): Matcher found a match AND the expected match is correct.
  - False Positive (FP): Matcher found a match BUT it was wrong or unexpected.
  - False Negative (FN): Matcher returned None BUT a match was expected.
  - True Negative  (TN): Matcher returned None AND no match was expected.

  Precision = TP / (TP + FP)   -- "of what we matched, how much was right?"
  Recall    = TP / (TP + FN)   -- "of what should match, how much did we find?"
  F1        = 2 * P * R / (P + R)

Usage:
    from ingestion.ocr.evaluator import OCREvaluator
    from knowledge_base.matcher_evaluator import MatcherEvaluator, EvalSample

    evaluator = MatcherEvaluator()
    samples = [
        EvalSample(raw="soya lecithin",       expected_name="Soy Lecithin"),
        EvalSample(raw="e322",                expected_name="Soy Lecithin"),
        EvalSample(raw="xyz_unknown_chem123", expected_name=None),
    ]
    report = evaluator.evaluate(samples)
    print(report)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict

# Import the matcher we are evaluating
from knowledge_base.matcher import IngredientMatcher


@dataclass
class EvalSample:
    """
    A single labelled evaluation sample for the ingredient matcher.

    Attributes:
        raw:           Raw ingredient string as it would appear on a food label
                       or come from OCR output.
        expected_name: Canonical ingredient name expected from the matcher
                       (exactly as stored in ingredients_seed.json 'name' field).
                       Set to None if NO match is expected (unknown ingredient).
    """
    raw: str
    expected_name: Optional[str]


class MatcherEvaluator:
    """
    Evaluates IngredientMatcher precision, recall, and F1-score against a
    hand-labelled dataset of raw ingredient strings.

    A match is considered a True Positive when:
      - The matcher returns a non-None result AND
      - result['name'] == sample.expected_name (case-insensitive).

    A match is considered a False Positive when:
      - The matcher returns a non-None result BUT
      - result['name'] != sample.expected_name, OR expected_name is None.

    A match is considered a False Negative when:
      - The matcher returns None BUT sample.expected_name is not None.

    A match is considered a True Negative when:
      - The matcher returns None AND sample.expected_name is None.
    """

    def __init__(self, score_cutoff: float = 80.0):
        """
        Args:
            score_cutoff: Fuzzy matching threshold passed to IngredientMatcher.
        """
        self._matcher = IngredientMatcher()
        self._score_cutoff = score_cutoff

    def evaluate(self, samples: List[EvalSample]) -> Dict:
        """
        Run the matcher against all samples and compute classification metrics.

        Args:
            samples: List of EvalSample objects with raw strings and expected names.

        Returns:
            Dict containing:
              - "precision":   float [0.0, 1.0]
              - "recall":      float [0.0, 1.0]
              - "f1":          float [0.0, 1.0]
              - "tp", "fp", "fn", "tn": int counts
              - "n_samples":   int total samples
              - "accuracy":    float [0.0, 1.0]  -- (TP+TN) / N
              - "per_sample":  List of per-sample result dicts for detailed inspection.
        """
        tp = fp = fn = tn = 0
        per_sample_results = []

        for sample in samples:
            result = self._matcher.match_ingredient(
                sample.raw, score_cutoff=self._score_cutoff
            )
            matched_name = result["name"] if result is not None else None
            expected = sample.expected_name

            # Determine classification
            if matched_name is not None and expected is not None:
                if matched_name.lower() == expected.lower():
                    outcome = "TP"
                    tp += 1
                else:
                    outcome = "FP"
                    fp += 1
            elif matched_name is None and expected is not None:
                outcome = "FN"
                fn += 1
            elif matched_name is None and expected is None:
                outcome = "TN"
                tn += 1
            else:
                # matched something when nothing was expected
                outcome = "FP"
                fp += 1

            per_sample_results.append({
                "raw": sample.raw,
                "expected": expected,
                "matched": matched_name,
                "outcome": outcome,
            })

        # Compute metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0.0)
        n = len(samples)
        accuracy = (tp + tn) / n if n > 0 else 0.0

        return {
            "precision":  round(precision, 4),
            "recall":     round(recall, 4),
            "f1":         round(f1, 4),
            "accuracy":   round(accuracy, 4),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "n_samples":  n,
            "per_sample": per_sample_results,
        }

    def evaluate_and_print(self, samples: List[EvalSample]) -> Dict:
        """
        Evaluate and print a formatted report to stdout.

        Args:
            samples: List of EvalSample objects.

        Returns:
            Same dict as evaluate().
        """
        report = self.evaluate(samples)

        print("=" * 60)
        print("  Ingredient Matcher -- Evaluation Report (Member 1)")
        print("=" * 60)
        print(f"  Samples evaluated : {report['n_samples']}")
        print(f"  True  Positives   : {report['tp']}")
        print(f"  False Positives   : {report['fp']}")
        print(f"  False Negatives   : {report['fn']}")
        print(f"  True  Negatives   : {report['tn']}")
        print("-" * 60)
        print(f"  Precision         : {report['precision']:.4f}")
        print(f"  Recall            : {report['recall']:.4f}")
        print(f"  F1 Score          : {report['f1']:.4f}")
        print(f"  Accuracy          : {report['accuracy']:.4f}")
        print("=" * 60)

        # Show failures for debugging
        failures = [r for r in report["per_sample"] if r["outcome"] in ("FP", "FN")]
        if failures:
            print(f"\n  Failures ({len(failures)}):")
            for f in failures:
                print(f"    [{f['outcome']}] raw={f['raw']!r:30s} "
                      f"expected={str(f['expected'])!r:20s} "
                      f"got={str(f['matched'])!r}")

        return report
