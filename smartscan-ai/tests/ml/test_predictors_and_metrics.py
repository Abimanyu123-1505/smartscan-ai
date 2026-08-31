import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

import pytest
import numpy as np
from app.prediction.predictors import (
    PersistencePredictor,
    MarkovPredictor,
    LogisticPredictor,
    RandomForestPredictor,
    XGBoostPredictor,
    GRUPredictor,
    TransformerPredictor
)
from app.evaluation.ml_metrics import (
    ConfusionMatrix,
    compute_confusion_matrix,
    compute_accuracy,
    compute_precision,
    compute_recall,
    compute_f1,
    compute_pfa,
    compute_brier_score,
    compute_calibration_curve,
    evaluate_model_performance
)
from app.evaluation.cross_check import IndependentMetricVerifier, HandCalculatedFixtureValidator
from app.evaluation.leakage import LeakageValidator


def test_predictors_interface():
    predictors = [
        PersistencePredictor(),
        MarkovPredictor(),
        LogisticPredictor(),
        RandomForestPredictor(),
        XGBoostPredictor(),
        GRUPredictor(),
        TransformerPredictor()
    ]
    sample_seq = np.array([0, 1, 1, 0, 1, 0, 1, 1])

    for p in predictors:
        assert p.name is not None
        assert p.version is not None
        assert p.task is not None
        
        prob = p.predict_proba(sample_seq)
        pred = p.predict(sample_seq)
        
        assert 0.0 <= prob <= 1.0
        assert pred in (0, 1)


def test_hand_calculated_fixture():
    res = HandCalculatedFixtureValidator.validate_known_fixture()
    assert res["status"] == "PASS"
    assert res["accuracy"] == pytest.approx(0.960784, abs=1e-4)
    assert res["precision"] == pytest.approx(0.800000, abs=1e-4)
    assert res["recall"] == pytest.approx(0.800000, abs=1e-4)
    assert res["f1_score"] == pytest.approx(0.800000, abs=1e-4)
    assert res["pfa"] == pytest.approx(0.021739, abs=1e-4)


def test_metric_cross_checking():
    rng = np.random.RandomState(42)
    y_true = rng.binomial(1, 0.4, 200)
    y_prob = np.clip(y_true * 0.75 + rng.normal(0, 0.1, 200), 0.01, 0.99)
    y_pred = (y_prob >= 0.5).astype(int)

    prod = evaluate_model_performance(y_true, y_prob)
    passed, ver = IndependentMetricVerifier.verify_metrics(prod, y_true, y_pred)
    assert passed is True
    assert ver["max_difference"] < 1e-9


def test_calibration_curve():
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_prob = np.array([0.05, 0.15, 0.25, 0.35, 0.65, 0.75, 0.85, 0.95])
    cal = compute_calibration_curve(y_true, y_prob, num_bins=10)
    assert cal.ece >= 0.0
    assert len(cal.bins) == 11


def test_leakage_validator():
    report = LeakageValidator.validate_all()
    assert report.overall_status == "PASS"
    assert len(report.violations) == 0
