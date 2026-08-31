"""
tests.unit.test_sdr_and_labs
=============================
Pytest suite verifying SDR Hardware Abstraction Layer, ReceiverManager,
Uncertainty, Periodicity, Change Detection, Information Gain, VOI Mode,
Multi-Emitter Allocation, Counterfactual Replay, Ablation Lab, and Generalization Lab.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

import pytest
import numpy as np
from app.receiver.manager import ReceiverManager, ReceiverMode
from app.receiver.replay_receiver import ReplayReceiver
from app.receiver.rtlsdr_receiver import RTLSDRReceiver
from app.receiver.usrp_receiver import FutureUSRPReceiver
from app.intelligence.uncertainty_engine import UncertaintyEngine
from app.intelligence.periodicity_detector import PeriodicityDetector
from app.intelligence.change_detector import ChangeDetector
from app.intelligence.information_gain import InformationGainEngine
from app.intelligence.voi_mode import VOIEngine
from app.intelligence.multi_emitter import MultiEmitterAllocator, EmitterTarget
from app.evaluation.counterfactual import CounterfactualReplayEngine, DecisionSnapshot
from app.evaluation.ablation_lab import AblationLabEngine
from app.evaluation.generalization_lab import GeneralizationLabEngine
from app.evaluation.model_selection import ModelSelectionEngine


def test_receiver_manager_and_hal():
    mgr = ReceiverManager()
    assert mgr.mode == ReceiverMode.REAL_RF_REPLAY
    
    rx = mgr.get_receiver()
    assert isinstance(rx, ReplayReceiver)
    
    obs = rx.observe(freq_bin=2, time_slot=10)
    assert obs.frequency_bin == 2
    assert obs.time_slot == 10
    
    state = mgr.set_mode(ReceiverMode.LIVE_RTL_SDR)
    assert mgr.mode == ReceiverMode.LIVE_RTL_SDR
    assert state.is_connected is True
    
    state_dict = mgr.status()
    assert state_dict["mode"] == "LIVE_RTL_SDR"


def test_uncertainty_and_periodicity():
    u_res = UncertaintyEngine.evaluate_channel_uncertainty(0.5, 2.0, 2.0)
    assert 0.0 <= u_res["total_uncertainty_score"] <= 1.0

    p_res = PeriodicityDetector.detect_period([1, 0, 0, 1, 0, 0, 1, 0, 0, 1], current_slot=10)
    assert p_res["detected"] is True
    assert p_res["period_slots"] == 3


def test_change_detector_and_infogain():
    cd = ChangeDetector(threshold=0.35)
    res = cd.update(0.45)
    assert res["is_regime_shift"] is True
    assert "exploration increased" in res["message"]

    ig = InformationGainEngine.compute_information_gain(0.5, obs_count=2)
    assert 0.0 <= ig <= 1.0

    voi = VOIEngine.calculate_voi(freq_bin=1, predicted_prob=0.8, info_gain=0.4, uncertainty=0.2, periodicity_score=0.5, is_switched=True)
    assert "total_voi_utility" in voi


def test_multi_emitter_allocation():
    targets = [EmitterTarget("t1", 1, 1.0, "Wi-Fi"), EmitterTarget("t2", 4, 0.8, "BT")]
    alloc = MultiEmitterAllocator(targets)
    alloc.record_visit(1, True)
    alloc.record_visit(4, False)
    
    res = alloc.compute_fairness_and_coverage()
    assert res["total_visits"] == 2
    assert 0.0 <= res["jains_fairness_index"] <= 1.0


def test_labs_and_counterfactuals():
    cf = CounterfactualReplayEngine()
    snap = DecisionSnapshot(
        time_slot=5,
        selected_frequency_bin=1,
        selected_frequency_label="F2",
        observations_available={"power": -50},
        model_predictions=[0.1]*8,
        uncertainty_scores=[0.2]*8,
        periodicity_scores=[0.0]*8,
        info_gain_scores=[0.1]*8,
        candidate_utility_scores=[0.5]*8,
        natural_language_explanation="F2 selected",
        actual_ground_truth_state=1,
        actual_detection_outcome=True,
        revisit_gap_afterward=5
    )
    cf.log_snapshot(snap)
    res = cf.get_snapshot(5)
    assert res["selected_frequency_bin"] == 1

    ablation = AblationLabEngine.run_ablation_study()
    assert len(ablation["ablation_results"]) == 7

    gen = GeneralizationLabEngine.evaluate_generalization()
    assert "generalization_gap_f1" in gen

    ms = ModelSelectionEngine.select_best_model()
    assert ms["recommended_model"] == "GRU Neural Net"
