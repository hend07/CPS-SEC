"""
CPS-SEC Reproducibility Test Suite
====================================

Verifies that every numerical claim in the paper can be reproduced from
the data files in data/. Run with:

    python -m pytest tests/ -v

Or as a standalone script:

    python tests/test_paper_numbers.py

Author: Hind A. Al-Ghuraybi
License: MIT
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from maturity import (
    load_weights, load_models, load_scenarios,
    compute_global_weights, verify_unit_sum,
    compute_maturity, compute_all_models,
    CRITERIA_ORDER,
)
from sensitivity import (
    compute_rank_shift, compute_top_n_overlap,
    random_permutation_expected_shift,
    run_sensitivity_analysis,
)
from dimension_analysis import (
    compute_column_totals, compute_dimension_means,
    identify_lowest_criteria, compute_layer_means,
)

TOL = 1e-4


def test_unit_sum_baseline():
    """The baseline global weights must sum to exactly 1.0000"""
    weights = load_weights()
    dim_w = {d: meta["weight"] for d, meta in weights["dimensions"].items()}
    local_w = {c: meta["local_weight"] for c, meta in weights["criteria"].items()}
    global_weights = compute_global_weights(dim_w, local_w, weights["criteria"])
    total = sum(global_weights.values())
    assert abs(total - 1.0) < TOL, f"Sum is {total:.10f}, expected 1.0000"
    print(f"PASS  Baseline weights sum to {total:.4f}")


def test_unit_sum_all_scenarios():
    """All 5 scenarios must satisfy sum(global_weights) = 1.0000"""
    weights = load_weights()
    scenarios = load_scenarios()["scenarios"]
    for sname, scen in scenarios.items():
        gw = compute_global_weights(
            scen["dimension_weights"],
            scen["local_weights"],
            weights["criteria"],
        )
        total = sum(gw.values())
        assert abs(total - 1.0) < TOL, f"{sname}: sum is {total:.10f}"
        print(f"PASS  Scenario {sname} weights sum to {total:.4f}")


def test_global_weight_c1():
    """C1 global weight = 0.0875 (= 0.35 * 0.25)"""
    weights = load_weights()
    assert abs(weights["criteria"]["C1"]["global_weight"] - 0.0875) < TOL
    print(f"PASS  C1 global weight = 0.0875")


def test_global_weight_c11_highest():
    """C11 (Real-world Deployment) is the highest-weighted criterion at 0.1250"""
    weights = load_weights()
    assert abs(weights["criteria"]["C11"]["global_weight"] - 0.1250) < TOL
    print(f"PASS  C11 global weight = 0.1250 (highest)")


def test_global_weight_c5_lowest():
    """C5 (Robustness) is among the lowest at 0.0350"""
    weights = load_weights()
    assert abs(weights["criteria"]["C5"]["global_weight"] - 0.0350) < TOL
    print(f"PASS  C5 global weight = 0.0350")


def test_25_models_loaded():
    """The corpus must contain exactly 25 models"""
    models = load_models()
    assert len(models["models"]) == 25, f"Got {len(models['models'])} models"
    print(f"PASS  Corpus contains 25 models")


def test_every_model_has_16_scores():
    """Each model must have exactly 16 ordinal scores"""
    models = load_models()
    for m in models["models"]:
        assert len(m["scores"]) == 16, (
            f"{m['id']} has {len(m['scores'])} scores, expected 16"
        )
        for s in m["scores"]:
            assert s in (0, 0.5, 1), f"{m['id']}: invalid score {s}"
    print(f"PASS  All 25 models have 16 valid ordinal scores")


def test_paas_score():
    """PaaS achieves the top score of 0.6837 (the headline finding)"""
    weights = load_weights()
    models = load_models()
    results = compute_all_models(weights, models, "S0_Baseline")
    paas = next(r for r in results if r["model_id"] == "PaaS")
    assert paas["rank"] == 1, f"PaaS rank is #{paas['rank']}, expected #1"
    assert abs(paas["maturity"] - 0.6837) < TOL, (
        f"PaaS maturity is {paas['maturity']:.4f}, expected 0.6837"
    )
    assert paas["tier"] == "Advanced"
    print(f"PASS  PaaS top score = 0.6837 (Advanced tier)")


def test_vae_lstm_lowest():
    """VAE + LSTM has the lowest score of 0.2200"""
    weights = load_weights()
    models = load_models()
    results = compute_all_models(weights, models, "S0_Baseline")
    vae = next(r for r in results if r["model_id"] == "VAE + LSTM")
    assert vae["rank"] == 25
    assert abs(vae["maturity"] - 0.2200) < TOL
    print(f"PASS  VAE + LSTM lowest score = 0.2200 (#25)")


def test_three_lowest_criteria():
    """The three lowest-attainment criteria are C13, C7, C6 in that order"""
    models = load_models()
    totals = compute_column_totals(models)
    lowest = identify_lowest_criteria(totals, n=3)
    expected_ids = ["C13", "C7", "C6"]
    expected_totals = [1.5, 2.5, 6.5]
    for i, (crit, total) in enumerate(lowest):
        assert crit == expected_ids[i], (
            f"Position {i+1}: got {crit}, expected {expected_ids[i]}"
        )
        assert abs(total - expected_totals[i]) < TOL, (
            f"{crit}: got {total}, expected {expected_totals[i]}"
        )
    print(f"PASS  Lowest 3 criteria: C13=1.5, C7=2.5, C6=6.5")


def test_dimension_means():
    """Corpus-wide dimension means match Section 9.5 values"""
    weights = load_weights()
    models = load_models()
    means = compute_dimension_means(models, weights)
    expected = {
        "Security":    0.476,
        "Performance": 0.336,
        "Practical":   0.453,
        "Design":      0.593,
    }
    for dim, expected_val in expected.items():
        got = means[dim]
        assert abs(got - expected_val) < 0.005, (
            f"{dim}: got {got:.4f}, expected ~{expected_val:.3f}"
        )
        print(f"PASS  Dimension {dim:<14} mean = {got*100:.1f}% (expected ~{expected_val*100:.1f}%)")


def test_advanced_tier_models():
    """Exactly 2 models reach the Advanced tier: PaaS and HPCchain"""
    weights = load_weights()
    models = load_models()
    results = compute_all_models(weights, models, "S0_Baseline")
    advanced = [r for r in results if r["tier"] == "Advanced"]
    assert len(advanced) == 2, f"Got {len(advanced)} Advanced models"
    ids = {r["model_id"] for r in advanced}
    assert ids == {"PaaS", "HPCchain"}, f"Got {ids}"
    print(f"PASS  Exactly 2 Advanced-tier models: PaaS, HPCchain")


def test_no_mature_tier_models():
    """No model reaches the Mature tier (score >= 0.85)"""
    weights = load_weights()
    models = load_models()
    results = compute_all_models(weights, models, "S0_Baseline")
    mature = [r for r in results if r["tier"] == "Mature"]
    assert len(mature) == 0, f"Got {len(mature)} Mature models (should be 0)"
    print(f"PASS  No Mature-tier models (highest is PaaS at 0.6837)")


def test_paas_invariant_across_scenarios():
    """PaaS retains rank #1 in ALL 5 scenarios (key sensitivity claim)"""
    out = run_sensitivity_analysis()
    for sname, data in out["results"].items():
        paas_rank = next(r[1] for r in data["ranks"] if r[0] == "PaaS")
        assert paas_rank == 1, f"{sname}: PaaS rank is #{paas_rank}, expected #1"
    print(f"PASS  PaaS = #1 in all 5 scenarios (S0, S1, S2, S3, S4)")


def test_vae_lstm_invariant_across_scenarios():
    """VAE + LSTM retains rank #25 in ALL 5 scenarios"""
    out = run_sensitivity_analysis()
    for sname, data in out["results"].items():
        vae_rank = next(r[1] for r in data["ranks"] if r[0] == "VAE + LSTM")
        assert vae_rank == 25, f"{sname}: VAE+LSTM rank is #{vae_rank}, expected #25"
    print(f"PASS  VAE + LSTM = #25 in all 5 scenarios")


def test_avg_rank_shift_in_range():
    """Average rank shift falls within 1.5-1.8 positions (abstract claim)"""
    out = run_sensitivity_analysis()
    low, high = out["avg_shift_range"]
    assert 1.4 < low < 1.7, f"Low value {low} not in [1.4, 1.7]"
    assert 1.6 < high < 1.9, f"High value {high} not in [1.6, 1.9]"
    print(f"PASS  Average rank shift range = [{low:.2f}, {high:.2f}]  (~1.5 to 1.8)")
    for row in out["summary"]:
        print(f"      {row['scenario']:<28} avg_shift = {row['avg_shift']:.4f}")


def test_random_permutation_benchmark():
    """The observed shift should be ~20% of random-permutation expectation"""
    out = run_sensitivity_analysis()
    ratio = out["ratio_to_random"]
    assert 0.15 < ratio < 0.25, f"Ratio {ratio:.4f} outside expected [0.15, 0.25]"
    print(f"PASS  Observed shift = {ratio*100:.1f}% of random permutation expectation")


def run_all_tests():
    """Run every test and print a summary"""
    tests = [
        test_unit_sum_baseline,
        test_unit_sum_all_scenarios,
        test_global_weight_c1,
        test_global_weight_c11_highest,
        test_global_weight_c5_lowest,
        test_25_models_loaded,
        test_every_model_has_16_scores,
        test_paas_score,
        test_vae_lstm_lowest,
        test_three_lowest_criteria,
        test_dimension_means,
        test_advanced_tier_models,
        test_no_mature_tier_models,
        test_paas_invariant_across_scenarios,
        test_vae_lstm_invariant_across_scenarios,
        test_avg_rank_shift_in_range,
        test_random_permutation_benchmark,
    ]

    print("=" * 70)
    print("CPS-SEC REPRODUCIBILITY TEST SUITE")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    failures = []

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            failures.append((test.__name__, str(e)))
            print(f"FAIL  {test.__name__}: {e}")
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed (total: {len(tests)})")
    if failed == 0:
        print("All numerical claims in the paper are reproducible from this code.")
    else:
        print("FAILURES:")
        for name, err in failures:
            print(f"  - {name}: {err}")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
