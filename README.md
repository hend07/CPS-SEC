# CPS-SEC: Reproducibility Repository

[![Tests](https://img.shields.io/badge/tests-17%2F17%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

Reproducibility repository for the paper:

> **CPS-SEC: A Maturity-Driven Survey and Quantitative Evaluation Framework for Cyber-Physical Systems Security**
> Hind A. Al-Ghuraybi, King Abdulaziz University

This repository contains the complete data, computation code, and test suite for every numerical claim in the paper. Running `python tests/test_paper_numbers.py` will verify all 17 paper-level claims in under one second.

---

## Quick start

```bash
# Clone the repository
git clone https://github.com/<your-username>/cps-sec-reproducibility.git
cd cps-sec-reproducibility

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# No external dependencies are required - pure Python 3.8+

# Reproduce the baseline maturity ranking (Table in Section 9)
python src/maturity.py

# Reproduce the sensitivity analysis (Section 9.3)
python src/sensitivity.py

# Reproduce the dimension-level analysis (Section 9.5)
python src/dimension_analysis.py

# Run all reproducibility tests
python tests/test_paper_numbers.py
```

---

## The methodology in one paragraph

The CPS-SEC framework rests on a two-stage weighted scoring instrument. Sixteen criteria are grouped into four dimensions (Security, Performance, Practical, Design), each assigned a literature-grounded weight (35%, 25%, 25%, 15%). Within each dimension, criteria receive local weights that reflect their reported prevalence in the surveyed literature. The global weight of each criterion is the product of its dimension weight and its local weight, with the constraint that all 16 global weights sum to exactly 1.0000. For each surveyed model, the maturity score is computed as the weighted sum of ordinal evaluation scores (0, 0.5, or 1) across the 16 criteria, producing a dimensionless score in [0, 1] that can be compared across heterogeneous architectures.

```
maturity(model) = sum_{i=1..16} ( score_i × global_weight_i )

where global_weight_i = dimension_weight × local_weight_i
```

See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for the full derivation.

---

## Modifying the data

To re-evaluate a model with different scores:

1. Edit `data/models.json`
2. Change the `scores` array for the relevant model
3. Run `python tests/test_paper_numbers.py` to verify nothing else breaks
4. Run `python src/maturity.py` to see the updated ranking

To apply CPS-SEC to a new corpus:

1. Replace `data/models.json` with your own model scores
2. The framework is dimensionless, so weights in `data/weights.json` remain valid
3. All scripts will adapt automatically

---

## Citation

If you use this framework or this code, please cite the paper:

```bibtex
@article{alghuraybi2026cpssec,
  title   = {CPS-SEC: A Maturity-Driven Survey and Quantitative Evaluation Framework
             for Cyber-Physical Systems Security},
  author  = {Al-Ghuraybi, Hind A.},
  journal = {Under review},
  year    = {2026},
  note    = {Under review}
}
```

---

## License

The code in this repository is released under the MIT license. See [LICENSE](LICENSE) for details.

The framework methodology is described in the paper and may be freely reused, recalibrated, or extended for any research or industrial purpose.

---

## Contact

For questions about the framework, the methodology, or this repository, please open an issue on GitHub or contact the author at the email listed on the paper.
