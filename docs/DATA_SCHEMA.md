# Data Schema Documentation

This document describes the structure of the JSON files in `data/`. All files are valid JSON 7-bit ASCII (no special characters) and can be edited in any text editor.

---

## `data/weights.json`

Defines the CPS-SEC framework: dimensions, criteria, weights, and tier thresholds.

```json
{
  "dimensions": {
    "Security":    { "weight": 0.35, "rationale": "..." },
    "Performance": { "weight": 0.25, "rationale": "..." },
    "Practical":   { "weight": 0.25, "rationale": "..." },
    "Design":      { "weight": 0.15, "rationale": "..." }
  },
  "criteria": {
    "C1": {
      "name": "Layer Coverage",
      "dimension": "Security",
      "local_weight": 0.25,
      "global_weight": 0.0875
    },
    ...
  },
  "maturity_tiers": {
    "Mature":      { "min": 0.85, "max": 1.01, "stars": "*****" },
    "Advanced":    { "min": 0.65, "max": 0.85, "stars": "****" },
    "Developing":  { "min": 0.45, "max": 0.65, "stars": "***" },
    "Emerging":    { "min": 0.25, "max": 0.45, "stars": "**" },
    "Preliminary": { "min": 0.00, "max": 0.25, "stars": "*" }
  }
}
```

**Invariants:**
- `sum(dimensions[d].weight for d in dimensions) = 1.0`
- For each dimension `d`: `sum(criteria[c].local_weight for c in criteria if criteria[c].dimension == d) = 1.0`
- For each criterion: `global_weight = dimensions[dimension].weight * local_weight`
- `sum(criteria[c].global_weight for c in criteria) = 1.0000`

---

## `data/models.json`

Defines the 25 surveyed models and their ordinal scores against each criterion.

```json
{
  "models": [
    {
      "id": "PaaS",
      "ref": "[25]",
      "layer": "Application",
      "scores": [0, 1, 1, 0.5, 1, 0, 0, 1, 0.5, 0, 1, 1, 0.5, 1, 1, 1]
    },
    ...
  ]
}
```

**Fields:**
- `id` (string): Human-readable identifier for the model
- `ref` (string): Bibliography reference in square brackets
- `layer` (string): One of "Perception", "Network", "Application", "Multi-Layer"
- `scores` (array of 16 floats): Ordinal scores in `[0, 0.5, 1]` ordered as C1..C16

**Invariants:**
- Exactly 25 model entries
- Each `scores` array has exactly 16 elements
- Each score is one of {0, 0.5, 1}
- The order of scores matches `["C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12","C13","C14","C15","C16"]`

---

## `data/scenarios.json`

Defines the 5 weighting scenarios for the sensitivity analysis.

```json
{
  "scenarios": {
    "S0_Baseline": {
      "label": "Baseline (Security Priority)",
      "description": "...",
      "dimension_weights": {
        "Security":    0.35,
        "Performance": 0.25,
        "Practical":   0.25,
        "Design":      0.15
      },
      "local_weights": {
        "C1": 0.25, "C2": 0.30, ...
      }
    },
    "S1_EqualAll": { ... },
    "S2_PerformancePriority": { ... },
    "S3_PracticalPriority": { ... },
    "S4_DesignPriority": { ... }
  }
}
```

**Invariants:**
- Each scenario has exactly 4 dimension weights summing to 1.0
- Each scenario has exactly 16 local weights
- Within each dimension, local weights sum to 1.0
- The resulting global weights (dimension * local) sum to 1.0000 in every scenario

---

## Adding a new model

To evaluate an additional model:

1. Open `data/models.json`
2. Add a new entry to the `models` array following the schema above
3. Run `python tests/test_paper_numbers.py` to verify the structure
4. Run `python src/maturity.py` to see the updated ranking

Note that adding models will not affect the rankings of existing models (the framework is dimensionless), but corpus-wide statistics (dimension means, column totals) will change.

---

## Adding a new scenario

To explore a sector-specific weighting:

1. Open `data/scenarios.json`
2. Add a new scenario entry with valid dimension and local weights
3. Update `src/sensitivity.py` to include the new scenario in the analysis
4. Run `python src/sensitivity.py` to see the new rank shifts

---

## Editing weights

The framework is designed to be recalibrated for sector-specific deployments. To re-derive the weights:

1. Edit `data/weights.json` to change dimension or local weights
2. Manually update the `global_weight` field for each criterion (= dimension * local)
3. Run `python tests/test_paper_numbers.py` to verify the unit-sum constraint
4. Run `python src/maturity.py` for the updated ranking

The test suite will fail if the weights no longer sum to 1.0000.
