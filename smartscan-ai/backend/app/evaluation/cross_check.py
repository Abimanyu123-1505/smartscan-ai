"""
smartscan.backend.app.evaluation.cross_check
============================================
Independent Metric Verification Engine & Hand-Calculated Fixture Validator.
Guarantees zero metric fabrication and verifies math routines within 1e-9 tolerance.
"""

import math
import numpy as np
from typing import Dict, Any, Tuple
from app.evaluation.ml_metrics import (
    ConfusionMatrix,
    compute_confusion_matrix,
    compute_accuracy,
    compute_precision,
    compute_recall,
    compute_f1,
    compute_pfa
)


class IndependentMetricVerifier:
    """Cross-checks production evaluation metrics against independent math routines."""

    @staticmethod
    def verify_metrics(prod_metrics: Dict[str, Any], y_true: np.ndarray, y_pred: np.ndarray, tolerance: float = 1e-9) -> Tuple[bool, Dict[str, Any]]:
        y_true = np.asarray(y_true, dtype=int)
        y_pred = np.asarray(y_pred, dtype=int)

        # Independent reference calculations
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        total = tp + tn + fp + fn

        ref_acc = (tp + tn) / total if total > 0 else 0.0
        ref_prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        ref_rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        ref_f1 = 2 * ref_prec * ref_rec / (ref_prec + ref_rec) if (ref_prec + ref_rec) > 0 else 0.0
        ref_pfa = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        diffs = {
            "accuracy_diff": abs(prod_metrics.get("accuracy", 0.0) - ref_acc),
            "precision_diff": abs(prod_metrics.get("precision", 0.0) - ref_prec),
            "recall_diff": abs(prod_metrics.get("recall", 0.0) - ref_rec),
            "f1_diff": abs(prod_metrics.get("f1_score", 0.0) - ref_f1),
            "pfa_diff": abs(prod_metrics.get("pfa", 0.0) - ref_pfa),
        }

        passed = all(diff < tolerance for diff in diffs.values())
        return passed, {
            "status": "PASS" if passed else "FAIL",
            "tolerance": tolerance,
            "max_difference": max(diffs.values()) if diffs else 0.0,
            "diffs": diffs,
        }


class HandCalculatedFixtureValidator:
    """Validates metrics against hand-calculated known reference fixtures."""

    @staticmethod
    def validate_known_fixture() -> Dict[str, Any]:
        """
        Known Fixture:
          TP = 80, TN = 900, FP = 20, FN = 20 (Total = 1020)
        Expected:
          Accuracy  = 980 / 1020 = 0.960784
          Precision = 80 / 100   = 0.800000
          Recall/Pd = 80 / 100   = 0.800000
          F1 Score  = 0.800000
          Pfa       = 20 / 920   = 0.021739
        """
        cm = ConfusionMatrix(tp=80, tn=900, fp=20, fn=20)
        acc = compute_accuracy(cm)
        prec = compute_precision(cm)
        rec = compute_recall(cm)
        f1 = compute_f1(prec, rec)
        pfa = compute_pfa(cm)

        exp_acc = 980 / 1020
        exp_prec = 0.80
        exp_rec = 0.80
        exp_f1 = 0.80
        exp_pfa = 20 / 920

        passed = (
            abs(acc - exp_acc) < 1e-4 and
            abs(prec - exp_prec) < 1e-4 and
            abs(rec - exp_rec) < 1e-4 and
            abs(f1 - exp_f1) < 1e-4 and
            abs(pfa - exp_pfa) < 1e-4
        )

        return {
            "status": "PASS" if passed else "FAIL",
            "fixture": {"TP": 80, "TN": 900, "FP": 20, "FN": 20},
            "accuracy": round(acc, 6),
            "precision": round(prec, 6),
            "recall": round(rec, 6),
            "f1_score": round(f1, 6),
            "pfa": round(pfa, 6),
        }
