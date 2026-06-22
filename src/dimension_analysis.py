"""
CPS-SEC Dimension-Level Analysis
=================================

Computes corpus-wide attainment statistics per dimension and per criterion.

Key outputs reproduced from the paper:

  Dimension means (Section 9.5):
    Security:    47.6%
    Performance: 33.6%  (the lowest, identified as the priority deficit)
    Practical:   45.3%
    Design:      59.3%  (the highest)

  Three lowest-attainment criteria (Section 10.1):
    C13 Standards Compliance:  1.5 / 25
    C7  Energy Efficiency:     2.5 / 25
    C6  Resource Efficiency:   6.5 / 25

Author: Hind A. Al-Ghuraybi
License: MIT
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from maturity import (
    load_weights, load_models,
    CRITERIA_ORDER,
)


def compute_column_totals(models_data):
    """
    Compute the sum of scores for each criterion across all models.

    Returns:
        dict: {criterion_id: total_score, ...}
    """
    totals = {crit: 0.0 for crit in CRITERIA_ORDER}
    for model in models_data["models"]:
        for i, crit in enumerate(CRITERIA_ORDER):
            totals[crit] += model["scores"][i]
    return totals


def compute_dimension_means(models_data, weights_data):
    """
    Compute corpus-wide attainment ratio per dimension.

    For each dimension, the ratio is:
        sum(scores in dimension across all models) / (n_criteria * n_models)

    Returns:
        dict: {dimension_name: ratio, ...}  (ratios in [0, 1])
    """
    n_models = len(models_data["models"])
    by_dim = {}
    for crit, meta in weights_data["criteria"].items():
        by_dim.setdefault(meta["dimension"], []).append(crit)

    means = {}
    for dim, crits in by_dim.items():
        total_score = 0.0
        for model in models_data["models"]:
            for crit in crits:
                idx = CRITERIA_ORDER.index(crit)
                total_score += model["scores"][idx]
        max_possible = len(crits) * n_models
        means[dim] = round(total_score / max_possible, 4)
    return means


def identify_lowest_criteria(column_totals, n=3):
    """
    Identify the N criteria with the lowest corpus-wide attainment.

    Returns:
        list of tuples [(criterion_id, total), ...] sorted ascending by total
    """
    sorted_totals = sorted(column_totals.items(), key=lambda x: x[1])
    return sorted_totals[:n]


def identify_highest_criteria(column_totals, n=3):
    """
    Identify the N criteria with the highest corpus-wide attainment.

    Returns:
        list of tuples [(criterion_id, total), ...] sorted descending by total
    """
    sorted_totals = sorted(column_totals.items(), key=lambda x: -x[1])
    return sorted_totals[:n]


def compute_layer_means(models_data, weights_data):
    """
    Compute mean CPS-SEC maturity score per CPS layer.

    Returns:
        dict: {layer_name: mean_maturity, ...}
    """
    from maturity import compute_all_models
    results = compute_all_models(weights_data, models_data, "S0_Baseline")

    by_layer = {}
    for r in results:
        by_layer.setdefault(r["layer"], []).append(r["maturity"])

    means = {}
    for layer, scores in by_layer.items():
        means[layer] = {
            "n_models": len(scores),
            "mean_maturity": round(sum(scores) / len(scores), 4),
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
        }
    return means


def main():
    """Run the full dimension-level analysis and print results"""
    weights = load_weights()
    models = load_models()

    print("=" * 70)
    print("CPS-SEC DIMENSION-LEVEL ANALYSIS")
    print("=" * 70)
    print()

    print("Corpus-wide attainment ratio per dimension (Section 9.5):")
    print("-" * 50)
    dim_means = compute_dimension_means(models, weights)
    for dim in ["Security", "Performance", "Practical", "Design"]:
        ratio = dim_means[dim]
        bar = "#" * int(ratio * 40)
        print(f"  {dim:<14}: {ratio*100:5.1f}%  {bar}")
    print()

    print("Column totals (sum of scores per criterion across 25 models):")
    print("-" * 50)
    totals = compute_column_totals(models)
    for crit in CRITERIA_ORDER:
        crit_name = weights["criteria"][crit]["name"][:30]
        print(f"  {crit:<4} {crit_name:<32}: {totals[crit]:5.1f} / 25.0")
    print()

    print("Three LOWEST-attainment criteria (Section 10.1):")
    print("-" * 50)
    lowest = identify_lowest_criteria(totals, n=3)
    for crit, total in lowest:
        name = weights["criteria"][crit]["name"]
        print(f"  {crit}  {name:<40}: {total:.1f} / 25")
    print()

    print("Three HIGHEST-attainment criteria:")
    print("-" * 50)
    highest = identify_highest_criteria(totals, n=3)
    for crit, total in highest:
        name = weights["criteria"][crit]["name"]
        print(f"  {crit}  {name:<40}: {total:.1f} / 25")
    print()

    print("Mean CPS-SEC maturity per layer (Section 9.5, Table 13):")
    print("-" * 50)
    layer_means = compute_layer_means(models, weights)
    for layer in ["Perception", "Network", "Application", "Multi-Layer"]:
        if layer in layer_means:
            lm = layer_means[layer]
            print(f"  {layer:<14}  n={lm['n_models']:<4}  mean={lm['mean_maturity']:.4f}  "
                  f"range [{lm['min']:.4f}, {lm['max']:.4f}]")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
