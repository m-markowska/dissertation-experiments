# CanTIERr-2

CanTIERr-2 is the relaxed canonical tier learner introduced in Chapter 7 of
*Learning Phonological Transductions from Sparse Data over Structured
Representations*. It infers conservative tier content for 2-input-tier-based
strictly local (2-ITSL) transductions from input-output pairs.

The learner adapts the canonical-tier inference method developed by Burness
and McMullin (2019) for output-oriented 2-OTSL functions. Their method infers
a tier over the output alphabet. CanTIERr-2 transfers the central tier-removal
logic to the input-oriented 2-ITSL setting, where the tier is defined over the
input alphabet and can supply the structure required by input-based
transduction learners. The `r` denotes *relaxed*: the learner uses attested
continuations, bounded prefix-output estimates, and a double-witness condition
to avoid unsupported tier deletions in sparse samples. It therefore returns a
conservative tier rather than assuming that the sample contains every
extension required by the original identification procedure.

This repository contains the standalone learner, the Turkish backness and
roundness harmony data, and the four feature projections reported in the
dissertation. CanTIERr-2 uses only the Python standard library.

## Install

CanTIERr-2 requires Python 3.9 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Reproduce the Chapter 7 experiment

The experiment runners are dataset-independent. They read dataset paths and
ordered feature projections from a JSON configuration. The included default
configuration, `data/turkish/chapter7_experiments.json`, reproduces all four
Turkish conditions from Chapter 7:

```bash
python experiments/run_tier_learning.py \
  --config data/turkish/chapter7_experiments.json \
  --output /tmp/turkish_tiers.json
cmp /tmp/turkish_tiers.json results/turkish_tiers.json
```

`cmp` produces no output and exits successfully when the generated results
match the reference results. Individual targets can be selected by repeating
`--target`:

```bash
python experiments/run_tier_learning.py \
  --config data/turkish/chapter7_experiments.json \
  --target back --target round
```

Use `--verbose` to display PFEr prefix estimates and each tier-elimination
step. [RESULTS.md](RESULTS.md) relates the JSON output to dissertation Table
7.3.

## Quickstart

CanTIERr-2 accepts input-output sequences whose symbols are hashable. The
included projection helper constructs the dissertation representation from
the full Turkish feature pairs:

```python
from pathlib import Path

from cantier import cantier_r2, convert_backpairs
from cantier.data import project_pairs

data = Path("data/turkish")
projected = project_pairs(
    data / "pairs_features.tsv",
    data / "inventory_output.tsv",
    ["back", "tap"],
)
sample = convert_backpairs(projected, strip_right=False)
result = cantier_r2(sample)

print("Learned tier:", sorted(result.theta, key=str))
```

The first selected feature is the predicted output feature. All selected
features, in the supplied order, define the projected input symbols.

## Data

`data/turkish/` contains 265 reconstructed input-output pairs:

- `raw_surface_gloss.csv`: source-oriented surface forms and glosses;
- `raw_ur_sr_gloss.csv`: reconstructed underlying and surface forms;
- `pairs_segments.tsv`: boundary-marked segment pairs;
- `pairs_features.tsv`: complete feature-bundle pairs;
- `inventory_input.tsv`: input inventory, including underspecified `I` and
  `E`;
- `inventory_output.tsv`: surface inventory.

The experiment excludes hiatus-resolution cases involving `j` epenthesis and
collapses vowel length, following Chapter 7. Projection can map multiple full
pairs to the same reduced pair; the experiment retains the first occurrence of
each projected pair. This produces 64 unique pairs for back and front, 160 for
low, and 178 for round.

[DATA.md](DATA.md) documents provenance and formats. To rebuild the prepared
segment and feature files from the reconstructed CSV, run:

```bash
python experiments/prepare_data.py \
  data/turkish/raw_ur_sr_gloss.csv \
  data/turkish/inventory_input.tsv \
  data/turkish/inventory_output.tsv \
  /tmp/turkish-prepared \
  --inventory-alias 'č=t͡ʃ' \
  --inventory-alias 'y=j'
```

The preparation utility takes all paths and transcription aliases from the
command line. `--segment-alias` rewrites symbols in the prepared segment file;
`--inventory-alias` changes only feature-inventory lookup. Another language
can therefore be prepared without code changes.

## Configure another dataset

A new language requires prepared feature pairs, a compatible feature
inventory, and a JSON experiment file. Paths are interpreted relative to the
JSON file:

```json
{
  "pairs": "pairs_features.tsv",
  "inventory": "inventory_output.tsv",
  "configurations": {
    "target-name": ["predicted-feature", "context-feature"]
  }
}
```

The first feature in each configuration is the predicted output feature. The
complete ordered list defines the projected input symbols. The same
configuration can be passed to either `run_tier_learning.py` or
`run_tier_seal_pipeline.py`; no language-specific code is required.

## Reproduce the CanTIERr-2 to SEAL pipeline

Chapter 7 combines learned tier content with a canonical 2-ITSL transducer and
uses SEAL to learn the transition outputs. Install both sibling packages from
the root of the `dissertation-experiments` repository:

```bash
python -m pip install -e equational-learner -e cantier-r2
python cantier-r2/experiments/run_tier_seal_pipeline.py \
  --config cantier-r2/data/turkish/chapter7_experiments.json \
  --output /tmp/turkish_seal_pipeline.json
cmp /tmp/turkish_seal_pipeline.json \
  cantier-r2/results/turkish_seal_pipeline.json
```

The script learns each tier from the Turkish data, constructs its canonical
deterministic `k = 2` transducer, learns output mappings with PRD-SEAL, and
checks every training pair. PRD-SEAL is the relevant SEAL stage here because
the left-to-right tier context provides the structure needed for the
one-to-one alignment described in Section 7.4.2. See
[RESULTS.md](RESULTS.md) for the learned mappings and evaluation counts.

## Relationship to FxF and SEAL

CanTIERr-2 learns which input symbols belong on a tier. Given the learned tier
and fixed window size `k = 2`, this package constructs the canonical
deterministic transducer skeleton. SEAL then learns the output labels on that
skeleton.

These components have distinct roles:

- CanTIERr-2 infers tier content;
- FxF searches for useful feature representations;
- SEAL learns transition-output mappings for a fixed transducer structure.

Tier learning remains a standalone package with no mandatory dependency on FxF
or SEAL. Only the combined output-learning pipeline requires the sibling SEAL
package (`equational-learner`). FxF is not used by the Chapter 7 tier
experiment.

## Package interface

- `cantier.cantier_r2`: infer a conservative tier and return a
  `CanTierResult`;
- `cantier.convert_backpairs`: normalize boundary-marked projected pairs;
- `cantier.data.project_pairs`: construct a first-occurrence-unique feature
  projection from prepared data;
- `cantier.build_canonical_tier_transducer`: construct a deterministic `k = 2`
  skeleton from an alphabet and tier;
- `cantier.learn_tier_seal`: learn transition outputs for a supplied tier with
  PRD-SEAL;
- `cantier.learn_cantier_seal`: learn the tier and transition outputs in one
  pipeline.

All release functions have type annotations and structured input/output
documentation. Check the documentation contract with:

```bash
python tools/check_docstrings.py
```

## Citation and license

Citation metadata are provided in [CITATION.cff](CITATION.cff). The software
is distributed under the [MIT License](LICENSE).

CanTIERr-2 builds on:

> Burness, P., and K. McMullin. 2019. “Efficient Learning of Output
> Tier-Based Strictly 2-Local Functions.” In *Proceedings of the 16th Meeting
> on the Mathematics of Language*, 78–90.
