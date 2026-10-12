# Dataset provenance and formats

The textbook-style datasets were adapted from the collection identified as
Ellis et al. (2022) in the dissertation. Underlying representations were
reconstructed for these experiments. The source-specific filenames are
preserved here through this provenance table:

| Directory | Original source-oriented files | Pairs |
| --- | --- | ---: |
| `koasati` | `koasati_odden_81.csv`, `koasati_odden_81_URs.csv` | 28 |
| `kerewe` | `kerewe_odden_76-77.csv`, `kerewe_odden_76-77_URs.csv` | 48 |
| `lumasaaba` | `lumasaaba_roca_89.csv`, `lumasaaba_roca_89_URs.csv` | 14 |
| `samoan` | `samoan_odden_85.csv`, `samoan_odden_85_URs.csv` | 116 |
| `serbo_croatian` | `serbo-croatian_odden_4.1.csv`, `serbo-croatian_odden_4.1_URs.csv` | 132 |

The dissertation sentence assigning 48 pairs to Koasati and 28 to Kerewe
transposes these two counts. Both the raw and prepared files confirm the counts
shown above.

Prepared feature-pair rows encode an input as boundary-marked tuples of full
feature bundles. The output is feature-major: one output string per inventory
feature. R2L files reverse the internal input sequence and each output string.

Each textbook dataset also contains `fixed_specs.tsv`. These tables were
transcribed from the successful specifications in the preserved experiment
logs and are consumed by `experiments/run_textbook_full_sample.py`. Koasati,
Kerewe, and Lumasaaba use PRD-SEAL; Samoan and Serbo-Croatian use LCD-SEAL. The
recorded full-sample outcome is 25/25 successful features in both directions
except for Lumasaaba L2R (20/25); Lumasaaba R2L succeeds on all 25.

The Polish directory contains 5,003 pairs used in the reported experiment:
4,872 identity pairs and 131 non-identity pairs. Its release requires the
CHILDES and corpus citations given in the dissertation.

`experiments/run_polish_childes_cv.py` recreates the reported strict
identity-stratified ten-fold assignment with seed 13. Training rows retain
their source frequency order. The driver learns the fixed R2L specifications
with PRD-SEAL at sample 1 and cumulative batches of 10, stopping a
fold when all 25 feature projections and every held-out pair pass. The
`--verify-reference` option compares generated checkpoint metrics with the
preserved dissertation tables.

The frequency table contains 5,006 non-header rows. The experimental pair list
excludes `kolor`, `włoż`, and `założ`, producing the reported 5,003 examples.
The source workbook contains more than 44,000 rows. `frequency_selection.tsv`
lists the exact row numbers selected from its `Frequencies` sheet. Workbook
formula proportions are multiplied by the cached `Occurances!G4` total and
formatted to two decimal places by `experiments/extract_polish_frequencies.py`.
This reproduces `frequency_list.tsv` exactly. The three excluded forms are
listed in `experiments/prepare_polish.py`, making pair generation deterministic.

The converter stores the workbook and selection manifest together because the
curated frequency list cannot be recovered from the top of the workbook alone.
No formulas or source rows are inferred at run time beyond the recorded
selection.

## Redistribution and citation

The raw reconstructed textbook data and CHILDES-derived frequency workbook
are included for reproducibility. Cite the original textbook, CHILDES, and
corpus sources specified in the dissertation when using these datasets. The
repository is distributed under the MIT License; see `LICENSE`.
