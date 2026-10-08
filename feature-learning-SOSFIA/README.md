# Feature learning with SOSFIA

This repository contains SOSFIA and its feature-by-feature extension,
FxF(SOSFIA). The learner infers subsequential transducers from input-output
string pairs represented with phonological features.

The repository includes the implementation, experimental data for English,
Yawelmani, Chukchi, and Polish, and the results reported in the dissertation.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Basic example

Run the following from the repository root after installation:

```python
from pathlib import Path

from fxf_sosfia import FST_feature, Sosfia, convert_data
from fxf_sosfia import preprocessing

data = Path("data/english")
sigma_path = data / "inventory_input.tsv"
delta_path = data / "inventory_output.tsv"
pairs_path = data / "pairs_features.tsv"
k = 2

sigma = preprocessing.sigma(str(sigma_path))
delta = preprocessing.delta(str(delta_path))
features = preprocessing.features(str(sigma_path))
states = preprocessing.states_gen(sigma, k)
transitions = preprocessing.transitions_gen(sigma, k, str(sigma_path))

initial_fst = FST_feature(
    states, sigma, delta, "<<", ">", transitions, features
)
training_pairs = convert_data(str(pairs_path))
learner = Sosfia(training_pairs, initial_fst, features)

learned_transitions = learner.fill_in_trans()
print(f"Learned {len(learned_transitions)} transitions")
```

## AMSSA sample search

AMSSA searches for a near-minimal sufficient sample. This example runs one
English experiment for `[nasal, cons]`, learns the value of *k*, and adds 10
pairs per sampling iteration:

```bash
python feat_test.py --language english --direction L2R --k-mode learned \
  --feature nasal cons --batch-size 10 --seed 1
```

Change `--direction` to `R2L`, or use `--k-mode fixed` to supply the known
locality value for the selected language. To let the search add features to an
insufficient specification, pass a single starting feature, such as
`--feature nasal`. Some searches can take several hours.

## Data

The experiments use the feature-pair files in `data/`. The raw segment pairs
are retained only as source data from which those files were generated. See
`data/FILE_MAP.tsv` for a complete file listing.

To verify that the feature-pair files can be regenerated from the segment data
and inventories, run:

```bash
python experiments/verify_data.py
```

## Results

The final results from the dissertation's Appendix B are available as TSV
files in `results/reference/`. See `RESULTS.md` for reproducibility details.

## Citation

Markowska, Magdalena. *Learning Phonological Transductions from Sparse Data
over Structured Representations*. Doctoral dissertation, Stony Brook
University, 2026.
