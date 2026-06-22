"""
Export computed results to CSV files in results/ for spreadsheet review.

Usage:
    python scripts/export_csv.py

Generates:
    results/baseline_ranking.csv     25 models ranked by S0 maturity
    results/sensitivity_results.csv  25 models x 5 scenarios
    results/dimension_means.csv      Corpus-wide dimension means
    results/column_totals.csv        Sum of scores per criterion
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from maturity import load_weights, load_models, compute_all_models, CRITERIA_ORDER
from sensitivity import run_sensitivity_analysis
from dimension_analysis import compute_column_totals, compute_dimension_means, compute_layer_means


def export_baseline_ranking():
    """Export the S0 baseline ranking to CSV"""
    weights = load_weights()
    models = load_models()
    results = compute_all_models(weights, models, "S0_Baseline")

    out_path = REPO / "results" / "baseline_ranking.csv"
    out_path.parent.mkdir(exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Model", "Ref", "Layer", "Maturity", "Tier"])
        for r in results:
            writer.writerow([
                r["rank"], r["model_id"], r["ref"], r["layer"],
                f"{r['maturity']:.4f}", r["tier"],
            ])

    print(f"Wrote {out_path}")


def export_sensitivity_results():
    """Export the full sensitivity analysis to CSV (25 rows x 5 scenarios)"""
    out = run_sensitivity_analysis()

    scenario_order = ["S0_Baseline", "S1_EqualAll", "S2_PerformancePriority",
                      "S3_PracticalPriority", "S4_DesignPriority"]

    model_ids = [r[0] for r in out["results"]["S0_Baseline"]["ranks"]]
    rank_score_by_model = {mid: {} for mid in model_ids}

    for sname in scenario_order:
        for model_id, rank, maturity in out["results"][sname]["ranks"]:
            rank_score_by_model[model_id][sname] = (rank, maturity)

    out_path = REPO / "results" / "sensitivity_results.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["Model"]
        for sname in scenario_order:
            header.append(f"{sname}_rank")
            header.append(f"{sname}_maturity")
        writer.writerow(header)

        baseline_rank = {mid: rank_score_by_model[mid]["S0_Baseline"][0]
                         for mid in model_ids}
        sorted_models = sorted(model_ids, key=lambda m: baseline_rank[m])

        for mid in sorted_models:
            row = [mid]
            for sname in scenario_order:
                rank, score = rank_score_by_model[mid][sname]
                row.append(rank)
                row.append(f"{score:.4f}")
            writer.writerow(row)

    print(f"Wrote {out_path}")


def export_dimension_means():
    """Export corpus-wide dimension means and layer means to CSV"""
    weights = load_weights()
    models = load_models()
    dim_means = compute_dimension_means(models, weights)
    layer_means = compute_layer_means(models, weights)

    out_path = REPO / "results" / "dimension_means.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Section", "Group", "Statistic", "Value"])
        for dim in ["Security", "Performance", "Practical", "Design"]:
            writer.writerow(["Section 9.5", f"Dimension: {dim}",
                             "Mean attainment", f"{dim_means[dim]:.4f}"])
            writer.writerow(["Section 9.5", f"Dimension: {dim}",
                             "Mean attainment (%)", f"{dim_means[dim]*100:.1f}"])
        for layer in ["Perception", "Network", "Application", "Multi-Layer"]:
            if layer in layer_means:
                lm = layer_means[layer]
                writer.writerow(["Section 9.5", f"Layer: {layer}",
                                 "n_models", lm["n_models"]])
                writer.writerow(["Section 9.5", f"Layer: {layer}",
                                 "Mean maturity", f"{lm['mean_maturity']:.4f}"])

    print(f"Wrote {out_path}")


def export_column_totals():
    """Export sum of scores per criterion across all 25 models"""
    weights = load_weights()
    models = load_models()
    totals = compute_column_totals(models)

    out_path = REPO / "results" / "column_totals.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Criterion", "Name", "Dimension", "Total (/25)", "Attainment %"])
        for crit in CRITERIA_ORDER:
            meta = weights["criteria"][crit]
            total = totals[crit]
            attainment = total / 25 * 100
            writer.writerow([
                crit, meta["name"], meta["dimension"],
                f"{total:.1f}", f"{attainment:.1f}",
            ])

    print(f"Wrote {out_path}")


def main():
    print("Exporting CSV files to results/...")
    print()
    export_baseline_ranking()
    export_sensitivity_results()
    export_dimension_means()
    export_column_totals()
    print()
    print("Done. Open the CSV files in Excel, Numbers, or Google Sheets.")


if __name__ == "__main__":
    main()
