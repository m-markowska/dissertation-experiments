# Factor by Feature (FxF) with SEAL

This repository contains the Factor by Feature architecture, the SEAL learner,
the naturalistic experiments from Chapter 6, and the raw and prepared forms of
every dataset used by those experiments.

See [RESULTS.md](RESULTS.md) for headline findings, verification status, and a
map from dissertation tables to machine-readable result files.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The core learner uses only the Python standard library.

## Architecture and terminology

Factor by Feature (FxF) and SEAL are different layers of the learning system:

- **FxF** is the learner-agnostic architecture introduced in Chapter 3. It
  decomposes a segmental transduction into feature-level transducers
  `tau(Phi, phi)`, one for each target output feature `phi`. FxF can use any
  feature learner that accepts a projected sample and returns a compatible
  feature-level transducer; SOSFIA and SEAL are two such learners in the
  dissertation.
- **SEAL** is the String Equation Adaptive Learner introduced in Chapter 5.
  For fixed `Phi`, `phi`, `k`, and processing direction, it constructs a k-ISL
  transducer skeleton, encodes transition outputs as placeholders, infers a
  consistent placeholder-to-string mapping, and returns one learned
  feature-level transducer.
- **PRD-SEAL** is SEAL's local Push-Right Distribution mode.
- **LCD-SEAL** is SEAL's global Length-Constrained Distribution mode.

`seal.learn_seal` performs one fixed-parameter SEAL run. `seal.learn_fxf`
implements the outer FxF search and uses SEAL by default; its
`feature_learner` argument permits another learner with the same callable
interface. The public modules `seal.learner` and `seal.fxf` keep these layers
separate.

## Run

```bash
python experiments/run_fixed.py --preset serbo_croatian_lat
```

To reproduce the recorded full-sample conditions for Koasati, Kerewe,
Lumasaaba, Samoan, and Serbo-Croatian:

```bash
python experiments/run_textbook_full_sample.py
```

The command writes feature-level and condition-level TSVs under `results/` and
returns a nonzero status if a condition differs from its recorded count. It
reproduces 25/25 feature specifications in both directions for four languages.
Lumasaaba reproduces 20/25 L2R and 25/25 R2L; the successful R2L direction is
the dissertation condition. Use `--language` or `--direction` for a partial
run.

## Quickstart: learn one feature-level transducer with SEAL

`learn_seal` learns `tau(Phi, phi)` for a supplied feature projection and `k`.
The first feature in the list is the target `phi`; the complete list is the
input projection `Phi`. This example uses LCD-SEAL with the included
Serbo-Croatian data:

```python
from pathlib import Path

from seal import learn_seal

data = Path("data/serbo_croatian")
status, details = learn_seal(
    ["cons", "lat"],
    str(data / "inventory.tsv"),  # input feature inventory
    str(data / "inventory.tsv"),  # output feature inventory
    str(data / "pairs_features_l2r.tsv"),
    3,                             # k
    direction="L2R",
    mode="lcd-seal",
)
print(status)
if status != "passed":
    print(details.get("error_msg", details))
```

Run the snippet from the repository root after `pip install -e .`. For an
automatic FxF search over target features, feature sets, and `k`, see
`learn_fxf` in the public API below. The `feature_learner` callback makes the
architecture independent of SEAL. Use `experiments/run_fixed.py` for a
recorded SEAL configuration.

To rerun the recorded five-fold Serbo-Croatian fixed-specification evaluation:

```bash
python experiments/run_serbo_croatian_cv.py --spec-set final \
  --output results/serbo-croatian-fixed-spec-cv.tsv
```

Use `--spec-set final-my-feat` to run the alternate specification set. The
optional `--target-feature` argument is useful for a partial check; pair-level
summary columns then aggregate only the selected specifications.

The evaluation follows the dissertation code's first-occurrence projection
rule: duplicate pairs created by projecting full feature bundles onto one
specification are evaluated once. With seed 13, the `final` specification set
reproduces the reported fold accuracies.

The Polish fixed specifications are available as `polish_voice`,
`polish_high`, and `polish_tense`. Use `--direction R2L --mode prd-seal` to
match the reported Polish condition.

To rerun the complete Polish CHILDES experiment (10 stratified folds,
frequency-ordered cumulative batches of 10, seed 13, R2L PRD-SEAL):

```bash
python experiments/run_polish_childes_cv.py --verify-reference
```

This is a long experiment: it fits 25 feature transducers at every cumulative
checkpoint until each fold reaches perfect held-out accuracy. A short exact
check of the fold that succeeds after 110 examples is:

```bash
python experiments/run_polish_childes_cv.py \
  --fold 2 --max-sample 110 --verify-reference \
  --output-dir /tmp/seal-polish-fold-2
```

Generated tables are written to `results/polish-rerun/` by default. The
preserved reference tables remain unchanged in `results/`.

## Data

Each textbook dataset directory contains:

- the source transcription CSV;
- the reconstructed underlying/surface CSV;
- segment-pair TSV;
- forward and reversed feature-pair TSV;
- the feature inventories used for conversion.
- `fixed_specs.tsv`, containing the recorded feature sets and locality widths.

`data/polish_childes/` additionally contains the original frequency workbook,
the exact row-selection manifest, the frequency-ordered intermediate file, and
all prepared forms used in the 5,003-pair experiment. Regenerate the curated
frequency list from the workbook and manifest with:

```bash
python experiments/extract_polish_frequencies.py \
  data/polish_childes/raw_frequency_workbook.xlsx \
  data/polish_childes/frequency_selection.tsv \
  /tmp/frequency_list.tsv
```

Run `experiments/prepare_data.py` to regenerate prepared textbook data from a
reconstructed CSV. Run `experiments/prepare_polish.py` to regenerate Polish
segment pairs from the frequency list. `DATA.md` records the source files,
curation, aliases, and pair counts.

The fixed runner reproduces supplied specifications on the full training
datasets. Dedicated scripts rerun the Serbo-Croatian five-fold evaluation and
the Polish incremental ten-fold learning curve. See `DATA.md` for the exact
inputs and the scope of the preserved outputs.

## Public API

- `seal.learn_seal`: learn one feature-level transducer for supplied SEAL
  parameters.
- `seal.learn_fxf`: run the learner-agnostic FxF architecture; SEAL is the
  default feature learner.
- `seal.learn_prd_seal`: infer placeholder outputs using PRD-SEAL.
- `seal.learn_lcd_seal`: infer placeholder outputs using LCD-SEAL.

The historical names `learn_one_feat`, `flex_learn`, `learner_identity`, and
`learn_kisl_dsf` remain importable for older research scripts, but they are not
part of the documented public API.

The files under `results/` are reference outputs rather than inputs to the
learner.

## Citation

The software accompanies:

> Magdalena Markowska. 2026. *Learning Phonological Transductions from Sparse
> Data over Structured Representations*. PhD dissertation, Stony Brook
> University.

The textbook-style datasets were adapted from Ellis, Albright,
Solar-Lezama et al. (2022), “Synthesizing theories of human language with
Bayesian program induction,” *Nature Communications* 13:5024. The Polish data
are derived from CHILDES; cite MacWhinney (2000), *The CHILDES Project: Tools
for Analyzing Talk*, third edition, together with the relevant corpus sources.

## License

This repository is distributed under the MIT License. See `LICENSE`.
