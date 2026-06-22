# CPS-SEC Methodology Documentation

This document describes the two-stage weighted scoring methodology underlying the CPS-SEC framework. Every numerical claim in the paper follows from this methodology applied to the data in `data/`.

---

## 1. The framework

CPS-SEC evaluates each cyber-physical system security model against 16 criteria, grouped into 4 dimensions:

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Security | 0.35 | C1 Layer Coverage, C2 Threat Coverage, C3 Privacy, C4 Adaptability, C5 Robustness |
| Performance | 0.25 | C6 Resource Efficiency, C7 Energy Efficiency, C8 Detection Accuracy, C9 Scalability, C10 Response Time |
| Practical | 0.25 | C11 Real-world Deployment, C12 Interoperability, C13 Standards Compliance |
| Design | 0.15 | C14 Explainability, C15 Data Quality, C16 Modularity |

Each criterion receives an ordinal score per model: 0 (not addressed), 0.5 (partially addressed), or 1 (fully addressed with documented evidence).

---

## 2. Two-stage weighting

The maturity score is computed using two-stage normalization:

### Stage 1: Dimension-level allocation

Each dimension receives a global weight reflecting its overall importance:

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Security | 0.35 | Aligns with NIST CSF (Protect function), IEC 62443 (Security Levels), and ISO/IEC 27001 (information security as primary concern) |
| Performance | 0.25 | Equal to Practical; reflects edge-computing constraints on CPS deployments |
| Practical | 0.25 | Equal to Performance; reflects the importance of real-world deployment for industrial CPS |
| Design | 0.15 | Lower weight; design-quality criteria are supplementary to security efficacy |

Constraint:
```
sum(dimension_weights) = 0.35 + 0.25 + 0.25 + 0.15 = 1.00
```

### Stage 2: Within-dimension local weights

Within each dimension, criteria receive local weights that reflect their reported prevalence in the surveyed literature:

**Security (5 criteria, sum = 1.00):**
| Criterion | Local Weight | Rationale |
|-----------|--------------|-----------|
| C2 Threat Coverage | 0.30 | Most prevalent security measure in the corpus |
| C1 Layer Coverage | 0.25 | Second-most prevalent |
| C4 Adaptability | 0.20 | Zero-day resilience increasingly important |
| C3 Privacy | 0.15 | Partly covered by C2 |
| C5 Robustness | 0.10 | Least frequently tested in the corpus |

**Performance (5 criteria, sum = 1.00):**
| Criterion | Local Weight | Rationale |
|-----------|--------------|-----------|
| C6 Resource Efficiency | 0.30 | Primary deployability constraint |
| C8 Detection Accuracy | 0.25 | Core performance quality |
| C7 Energy Efficiency | 0.15 | Critical for battery-constrained CPS |
| C9 Scalability | 0.15 | Important for industrial deployments |
| C10 Response Time | 0.15 | Critical for real-time CPS |

**Practical (3 criteria, sum = 1.00):**
| Criterion | Local Weight | Rationale |
|-----------|--------------|-----------|
| C11 Real-world Deployment | 0.50 | Strongest signal of maturity |
| C12 Interoperability | 0.30 | Important for IT/OT convergence |
| C13 Standards Compliance | 0.20 | Required for regulated industries |

**Design (3 criteria, sum = 1.00):**
| Criterion | Local Weight | Rationale |
|-----------|--------------|-----------|
| C14 Explainability | 0.40 | Highest in XAI-driven era |
| C15 Data Quality | 0.35 | Critical for ML-based models |
| C16 Modularity | 0.25 | Important for architectural reuse |

### Stage 3: Global weight as product

The global weight of each criterion is the product of its dimension weight and its local weight:

```
global_weight(C_i) = dimension_weight(D) × local_weight(C_i within D)
```

For example, C1 Layer Coverage:

```
global_weight(C1) = 0.35 × 0.25 = 0.0875
```

This produces 16 global weights that sum to exactly 1.0000.

---

## 3. Maturity score

The CPS-SEC maturity score for a given model is the weighted sum of its ordinal scores across all 16 criteria:

```
maturity(model) = sum_{i=1..16} ( score_i × global_weight_i )
```

Because all scores are in [0, 1] and all weights sum to 1, the maturity score lies in [0, 1].

### Worked example: PaaS

| Criterion | Score | Global Weight | Contribution |
|-----------|-------|---------------|--------------|
| C1 | 0    | 0.0875 | 0.0000 |
| C2 | 1    | 0.1050 | 0.1050 |
| C3 | 1    | 0.0525 | 0.0525 |
| C4 | 0.5  | 0.0700 | 0.0350 |
| C5 | 1    | 0.0350 | 0.0350 |
| C6 | 0    | 0.0750 | 0.0000 |
| C7 | 0    | 0.0375 | 0.0000 |
| C8 | 1    | 0.0625 | 0.0625 |
| C9 | 0.5  | 0.0375 | 0.0188 |
| C10 | 0   | 0.0375 | 0.0000 |
| C11 | 1   | 0.1250 | 0.1250 |
| C12 | 1   | 0.0750 | 0.0750 |
| C13 | 0.5 | 0.0500 | 0.0250 |
| C14 | 1   | 0.0600 | 0.0600 |
| C15 | 1   | 0.0525 | 0.0525 |
| C16 | 1   | 0.0375 | 0.0375 |
| **Total** | | **1.0000** | **0.6837** |

PaaS achieves a maturity score of 0.6837, which falls into the Advanced tier ([0.65, 0.85)).

---

## 4. Tier classification

| Tier | Range | Stars |
|------|-------|-------|
| Mature | [0.85, 1.00] | ★★★★★ |
| Advanced | [0.65, 0.85) | ★★★★ |
| Developing | [0.45, 0.65) | ★★★ |
| Emerging | [0.25, 0.45) | ★★ |
| Preliminary | [0.00, 0.25) | ★ |

In the surveyed corpus:
- 0 models reach Mature
- 2 models reach Advanced (PaaS, HPCchain)
- 13 models reach Developing
- 9 models reach Emerging
- 1 model reaches Preliminary

---

## 5. Sensitivity analysis

To verify that the rankings are not artifacts of the specific weighting scheme, the framework is re-applied under five distinct scenarios:

| Scenario | Dimension Weights | Local Weights | Purpose |
|----------|-------------------|---------------|---------|
| S0 Baseline | Security 35%, others as above | As in Table 7 | The paper's main scheme |
| S1 Equal Weights | All 25% | All equal within dimension | No a-priori prioritization |
| S2 Performance Priority | Performance 35% | As in S0 | Edge devices, real-time CPS |
| S3 Practical Priority | Practical 35% | As in S0 | Industrial deployment focus |
| S4 Design Priority | Design 35% | As in S0 | XAI-focused research |

In all scenarios, the global weights sum to exactly 1.0000 by construction.

### Rank shift formula

For each model i and each scenario k, the rank shift relative to baseline is:

```
shift(i, k) = | rank(i, S0) - rank(i, Sk) |
```

The average rank shift for scenario k is:

```
avg_shift(k) = (1 / N) × sum_{i=1..N} shift(i, k)
```

where N = 25 (the number of surveyed models).

### Observed values

| Scenario | Models Changed | Total Shift | Avg Shift |
|----------|----------------|-------------|-----------|
| S1 Equal Weights | 17/25 | 40 | 1.60 |
| S2 Performance Priority | 20/25 | 44 | 1.76 |
| S3 Practical Priority | 20/25 | 38 | 1.52 |
| S4 Design Priority | 18/25 | 44 | 1.76 |
| **Range** | | | **1.52 to 1.76** |

The range of 1.5 to 1.8 positions reported in the abstract is the conservative rounding of this empirical range.

### Random-permutation benchmark

For a fully randomized permutation of N = 25 items, the expected absolute rank shift per item is approximately:

```
expected_random_shift ≈ (N+1)/3 = 26/3 ≈ 8.67 positions
```

The observed empirical shift of 1.5 to 1.8 positions represents approximately 19% of this random expectation, providing strong evidence that the rankings reflect genuine differences in evaluation evidence rather than weight-dependent artifacts.

---

## 6. Reproducibility

Every value in this document is reproducible by running:

```bash
python tests/test_paper_numbers.py
```

The test suite verifies 17 distinct paper-level claims, all of which pass against the data in `data/`.

For per-claim reproduction instructions, see `docs/REPRODUCIBILITY.md`.
