# Dataset provenance and formats

## Source and preparation

The Turkish data are adapted from the dataset reported by Ellis et al. (2022),
*Synthesizing theories of human language with Bayesian program induction*,
*Nature Communications* 13, 5024. The source data contained surface forms and
glosses; underlying representations were reconstructed for the dissertation
experiments.

The Chapter 7 experiment contains 265 input-output pairs after removing forms
with vowel-hiatus resolution through `j` epenthesis. Vowel length is collapsed
because it does not determine the backness or roundness mappings examined in
the experiment.

## Files

| File | Contents | Data rows |
| --- | --- | ---: |
| `raw_surface_gloss.csv` | Surface forms and glosses | 265 |
| `raw_ur_sr_gloss.csv` | Reconstructed UR, SR, and gloss | 265 |
| `pairs_segments.tsv` | Prepared segment-level input-output pairs | 265 |
| `pairs_features.tsv` | Full feature-bundle input-output pairs | 265 |
| `inventory_input.tsv` | Input feature inventory | 28 segments |
| `inventory_output.tsv` | Surface feature inventory | 26 segments |
| `chapter7_experiments.json` | Dataset paths and named feature projections | 4 configurations |

The input inventory contains the underspecified symbols `I` and `E`. They are
absent from the surface inventory because their feature values are resolved in
the output.

## Prepared representations

Each row of `pairs_segments.tsv` has two tab-separated Python literals. The
first is a list of singleton input tuples with `<` and `>` boundaries; the
second is the corresponding list of output segments.

Each row of `pairs_features.tsv` also has two tab-separated literals. Its input
contains one complete feature-bundle string per segment. Its output is
feature-major: each string contains the values of one feature across the full
surface form.

`cantier.data.project_pairs` selects an ordered feature set from these complete
representations. The first selected feature supplies the output string, while
all selected features jointly define each input symbol. Projection-created
duplicates are removed in first-occurrence order, matching the dissertation
experiment pipeline.

## Experiment projections

| Target feature | Ordered input feature set | Unique projected pairs |
| --- | --- | ---: |
| back | back, tap | 64 |
| front | front, tap | 64 |
| low | low, back, tap | 160 |
| round | round, back, tap, high | 178 |

The prepared TSV files can be regenerated with
`experiments/prepare_data.py`; the complete command is given in `README.md`.
The experiment runners accept any configuration with the same JSON fields, so
additional languages do not require changes to the Python source.
