"""
CPS-SEC Maturity Score Computation
====================================

Computes the CPS-SEC maturity score for each model using the two-stage
weighted scoring methodology described in Section 8 of the paper.

Formula:
    Maturity(model) = sum_{i=1..16} ( score_i * global_weight_i )

Where:
    global_weight_i = dimension_weight * local_weight_i

This module is the single source of truth for all maturity computations
in the paper. Section 9 results and Appendix C tables are generated
from this module.

Author: Hind A. Al-Ghuraybi
License: MIT
"""

import json
from pathlib import Path


CRITERIA_ORDER = [
    "C1", "C2", "C3", "C4", "C5",
    "C6", "C7", "C8", "C9", "C10",
    "C11", "C12", "C13",
    "C14", "C15", "C16",
]


def load_weights(path="data/weights.json"):
    """Load the baseline CPS-SEC weights from data/weights.json"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_models(path="data/models.json"):
    """Load all 25 model scores from data/models.json"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenarios(path="data/scenarios.json"):
    """Load all 5 sensitivity scenarios from data/scenarios.json"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_global_weights(dimension_weights, local_weights, criteria_meta):
    """
    Compute global weights from dimension weights and local weights.

    Formula: global_weight = dimension_weight * local_weight

    Args:
        dimension_weights: dict mapping dimension name to weight (e.g. {"Security": 0.35, ...})
        local_weights: dict mapping criterion id to local weight (e.g. {"C1": 0.25, ...})
        criteria_meta: dict mapping criterion id to metadata (must contain "dimension" key)

    Returns:
        dict mapping criterion id to global weight
    """
    global_weights = {}
    for crit_id in CRITERIA_ORDER:
        dim = criteria_meta[crit_id]["dimension"]
        global_weights[crit_id] = dimension_weights[dim] * local_weights[crit_id]
    return global_weights


def verify_unit_sum(global_weights, tolerance=1e-6):
    """
    Verify that the global weights sum to 1.0 within the given tolerance.

    Raises:
        AssertionError: if the sum is not within tolerance of 1.0
    """
    total = sum(global_weights.values())
    assert abs(total - 1.0) < tolerance, (
        f"Global weights must sum to 1.0; got {total:.10f}"
    )
    return total


def compute_maturity(model_scores, global_weights):
    """
    Compute the CPS-SEC maturity score for a single model.

    Formula: maturity = sum_{i} ( score_i * global_weight_i )

    Args:
        model_scores: list of 16 ordinal scores in CRITERIA_ORDER order
        global_weights: dict mapping criterion id to global weight

    Returns:
        float: the maturity score (in [0, 1])
    """
    assert len(model_scores) == 16, (
        f"Expected 16 scores, got {len(model_scores)}"
    )
    maturity = 0.0
    for i, crit_id in enumerate(CRITERIA_ORDER):
        maturity += model_scores[i] * global_weights[crit_id]
    return round(maturity, 4)


def classify_tier(maturity_score, tiers):
    """
    Classify a maturity score into one of the five tiers.

    Args:
        maturity_score: float in [0, 1]
        tiers: dict mapping tier name to {min, max, stars} (from weights.json)

    Returns:
        tuple (tier_name, stars)
    """
    for name, bounds in tiers.items():
        if bounds["min"] <= maturity_score < bounds["max"]:
            return name, bounds["stars"]
    return "Unknown", "?"


def compute_all_models(weights_data, models_data, scenario_name="S0_Baseline"):
    """
    Compute maturity scores for all 25 models under a given scenario.

    Args:
        weights_data: parsed weights.json content
        models_data: parsed models.json content
        scenario_name: name of scenario to use (default S0_Baseline = paper's main scheme)

    Returns:
        list of dicts: [{model_id, layer, maturity, tier, stars, rank}, ...]
                       sorted by maturity descending; rank starts at 1
    """
    if scenario_name == "S0_Baseline":
        dim_w = {d: meta["weight"] for d, meta in weights_data["dimensions"].items()}
        local_w = {c: meta["local_weight"] for c, meta in weights_data["criteria"].items()}
    else:
        scenarios = load_scenarios()["scenarios"]
        assert scenario_name in scenarios, f"Unknown scenario: {scenario_name}"
        dim_w = scenarios[scenario_name]["dimension_weights"]
        local_w = scenarios[scenario_name]["local_weights"]

    global_weights = compute_global_weights(dim_w, local_w, weights_data["criteria"])
    verify_unit_sum(global_weights)

    results = []
    for model in models_data["models"]:
        maturity = compute_maturity(model["scores"], global_weights)
        tier, stars = classify_tier(maturity, weights_data["maturity_tiers"])
        results.append({
            "model_id": model["id"],
            "ref": model["ref"],
            "layer": model["layer"],
            "maturity": maturity,
            "tier": tier,
            "stars": stars,
        })

    results.sort(key=lambda r: -r["maturity"])
    
    # حساب الترتيب مع مراعاة القيم المتطابقة (Ties)
    for i in range(len(results)):
        if i > 0 and results[i]["maturity"] == results[i-1]["maturity"]:
            # إذا كانت القيمة مساوية للنموذج السابق، يأخذ نفس ترتيبه
            results[i]["rank"] = results[i-1]["rank"]
        else:
            # إذا كانت القيمة مختلفة، يأخذ الترتيب بناءً على موقعه في القائمة
            results[i]["rank"] = i + 1

    return results


def main():
    """Run the baseline computation and print the ranked table"""
    print("=" * 70)
    print("CPS-SEC MATURITY COMPUTATION - BASELINE (S0)")
    print("=" * 70)
    print()

    weights = load_weights()
    models = load_models()

    results = compute_all_models(weights, models, "S0_Baseline")

    print(f"{'Rank':<6}{'Model':<26}{'Layer':<14}{'Maturity':<11}{'Tier':<14}{'Stars'}")
    print("-" * 78)
    for r in results:
        print(f"#{r['rank']:<5}{r['model_id']:<26}{r['layer']:<14}{r['maturity']:<11.4f}{r['tier']:<14}{r['stars']}")

    print()
    print("=" * 70)
    print(f"Total models: {len(results)}")
    print(f"Top score: {results[0]['maturity']:.4f} ({results[0]['model_id']})")
    print(f"Lowest score: {results[-1]['maturity']:.4f} ({results[-1]['model_id']})")
    print("=" * 70)


if __name__ == "__main__":
    main()