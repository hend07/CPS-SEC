# Reproducibility Guide

This document maps every numerical claim in the paper to the exact code that reproduces it. To verify any specific claim, run the command listed in the corresponding row.

---

## Abstract claims

### Claim: "sixteen ordinally scored criteria grouped into Security, Performance, Practical, and Design dimensions"

```bash
python -c "
import json
with open('data/weights.json') as f:
    w = json.load(f)
print('Criteria:', len(w['criteria']))
print('Dimensions:', list(w['dimensions'].keys()))
"
```

Expected output:
```
Criteria: 16
Dimensions: ['Security', 'Performance', 'Practical', 'Design']
```

### Claim: "twenty-five peer-reviewed models published between 2019 and 2025"

```bash
python -c "
import json
with open('data/models.json') as f:
    m = json.load(f)
print('Models:', len(m['models']))
"
```

Expected output: `Models: 25`

### Claim: "no model attains the Mature tier, only two models reach the Advanced tier"

```bash
python src/maturity.py | grep -E "(Mature|Advanced)"
```

Expected output:
```
#1     PaaS                      Application    0.6837     Advanced
#2     HPCchain                  Multi-Layer    0.6540     Advanced
```

(Exactly 2 Advanced, 0 Mature)

### Claim: "Performance dimension trails at 33.6 percent corpus-wide attainment"

```bash
python src/dimension_analysis.py | grep Performance
```

Expected output:
```
  Performance   :  33.6%  #############
```

### Claim: "Standards Compliance (C13 = 1.5/25), Energy Efficiency (C7 = 2.5/25), and Resource Efficiency (C6 = 6.5/25)"

```bash
python src/dimension_analysis.py | grep -A 4 "LOWEST"
```

Expected output:
```
Three LOWEST-attainment criteria (Section 10.1):
--------------------------------------------------
  C13  Standards Compliance                    : 1.5 / 25
  C7   Energy Efficiency                       : 2.5 / 25
  C6   Resource Efficiency                     : 6.5 / 25
```

### Claim: "the highest-performing architecture achieved a baseline CPS-SEC score of 0.6837"

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from maturity import load_weights, load_models, compute_all_models
r = compute_all_models(load_weights(), load_models(), 'S0_Baseline')
print(f'Top score: {r[0][\"maturity\"]:.4f}  ({r[0][\"model_id\"]})')
"
```

Expected output: `Top score: 0.6837  (PaaS)`

### Claim: "average rank shift of only 1.5 to 1.8 positions"

```bash
python src/sensitivity.py | grep "AVERAGE RANK SHIFT"
```

Expected output:
```
AVERAGE RANK SHIFT RANGE: 1.52 to 1.76 positions
```

### Claim: "leading and trailing model rankings remained invariant across all five perturbed weight configurations"

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from sensitivity import run_sensitivity_analysis
out = run_sensitivity_analysis()
for sname, data in out['results'].items():
    paas = next(r for r in data['ranks'] if r[0] == 'PaaS')
    vae = next(r for r in data['ranks'] if r[0] == 'VAE + LSTM')
    print(f'{sname:<28} PaaS rank=#{paas[1]}   VAE+LSTM rank=#{vae[1]}')
"
```

Expected output:
```
S0_Baseline                  PaaS rank=#1   VAE+LSTM rank=#25
S1_EqualAll                  PaaS rank=#1   VAE+LSTM rank=#25
S2_PerformancePriority       PaaS rank=#1   VAE+LSTM rank=#25
S3_PracticalPriority         PaaS rank=#1   VAE+LSTM rank=#25
S4_DesignPriority            PaaS rank=#1   VAE+LSTM rank=#25
```

---

## Section 8 claims (Framework)

### Claim: "global weights are derived through a transparent two-stage methodology"

See `docs/METHODOLOGY.md` for the full derivation. To verify any specific global weight:

```bash
python -c "
import json
with open('data/weights.json') as f: w = json.load(f)
c = w['criteria']['C1']
dim_w = w['dimensions'][c['dimension']]['weight']
local_w = c['local_weight']
print(f'C1 dimension={c[\"dimension\"]} weight={dim_w}')
print(f'C1 local weight={local_w}')
print(f'C1 global weight={dim_w * local_w} (stored: {c[\"global_weight\"]})')
"
```

Expected output:
```
C1 dimension=Security weight=0.35
C1 local weight=0.25
C1 global weight=0.0875 (stored: 0.0875)
```

### Claim: "the global weights sum to exactly 1.0000 by construction"

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from maturity import load_weights, compute_global_weights
w = load_weights()
dim_w = {d: m['weight'] for d, m in w['dimensions'].items()}
local_w = {c: m['local_weight'] for c, m in w['criteria'].items()}
gw = compute_global_weights(dim_w, local_w, w['criteria'])
print(f'Sum of 16 global weights: {sum(gw.values()):.10f}')
"
```

Expected output: `Sum of 16 global weights: 1.0000000000`

---

## Section 9 claims (Empirical Application)

### Claim: "13 of 25 models reach the Developing tier"

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from collections import Counter
from maturity import load_weights, load_models, compute_all_models
r = compute_all_models(load_weights(), load_models(), 'S0_Baseline')
c = Counter(m['tier'] for m in r)
for tier in ['Mature', 'Advanced', 'Developing', 'Emerging', 'Preliminary']:
    print(f'{tier:<12}: {c[tier]}')
"
```

Expected output:
```
Mature      : 0
Advanced    : 2
Developing  : 13
Emerging    : 9
Preliminary : 1
```

### Claim: "Multi-Layer cohort mean = 0.5569"

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from dimension_analysis import compute_layer_means
from maturity import load_weights, load_models
lm = compute_layer_means(load_models(), load_weights())
for layer, stats in lm.items():
    print(f'{layer:<14}  n={stats[\"n_models\"]:<3}  mean={stats[\"mean_maturity\"]:.4f}')
"
```

Expected output:
```
Perception    n=7    mean=0.4740
Network       n=6    mean=0.4587
Application   n=4    mean=0.4553
Multi-Layer   n=8    mean=0.5569
```

---

## Section 9.3 claims (Sensitivity Analysis)

### Claim: "1.60 (S1), 1.76 (S2), 1.52 (S3), 1.76 (S4)"

```bash
python src/sensitivity.py | grep "avg_shift"
```

Expected output:
```
S1_EqualAll              17/25    40    1.60          3/3
S2_PerformancePriority   20/25    44    1.76          2/3
S3_PracticalPriority     20/25    38    1.52          2/3
S4_DesignPriority        18/25    44    1.76          3/3
```

### Claim: "~20% of the random-permutation expectation"

```bash
python src/sensitivity.py | grep -E "(Random|ratio)"
```

Expected output (approximately):
```
Random permutation expected shift (N=25): 8.65 positions
Observed / Random ratio:                  0.1922  (~19%)
```

---

## Section 10 claims (Future Directions)

### Claim: "C13 column total of 1.5/25 (lowest in framework)"

```bash
python src/dimension_analysis.py | grep "C13"
```

Expected output:
```
  C13  Standards Compliance                   :   1.5 / 25.0
  C13  Standards Compliance                    : 1.5 / 25
```

### Claim: "PUF+ZKP+BC reports 2,800 ms"

This is a literature-reported number (from the PUF+ZKP+BC paper), not computed from the framework. It is documented as the model's reported response time in the paper's main text.

---

## Running everything

To reproduce ALL claims in one command:

```bash
python tests/test_paper_numbers.py
```

This runs 17 test functions, each verifying a distinct paper claim. The expected output is:

```
RESULTS: 17 passed, 0 failed (total: 17)
All numerical claims in the paper are reproducible from this code.
```

If any test fails, the corresponding paper claim is not reproducible from the current data and code. This should never happen with the data as committed to this repository.
