# Experiment results

This file summarizes the Chapter 6 SEAL experiments and maps each headline
result to the machine-readable tables under `results/`. Detailed tables are
preserved as TSV rather than embedded in this document.

## Full-sample learning

All five textbook-style mappings were learned consistently with the observed
full sample. A condition is successful when all 25 output-feature mappings pass
in at least one processing direction. The fixed-specification rerun produced:

| Language | L2R features passed | R2L features passed | Successful condition |
| --- | ---: | ---: | --- |
| Koasati | 25/25 | 25/25 | both |
| Kerewe | 25/25 | 25/25 | both |
| Lumasaaba | 20/25 | 25/25 | R2L |
| Samoan | 25/25 | 25/25 | both |
| Serbo-Croatian | 25/25 | 25/25 | both |

The complete 250 feature/direction results are in
`results/textbook-full-sample.tsv`; the ten-condition summary is in
`results/textbook-full-sample-summary.tsv`.

Run:

```bash
python experiments/run_textbook_full_sample.py
```

## Serbo-Croatian held-out evaluation

The pair-level five-fold experiment uses seed 13 and separately evaluates L2R
and R2L transducers under learner-selected and manually imposed feature sets.
A pair is correct only when every feature projection recomposes to the correct
segmental output.

| Feature condition | L2R mean accuracy | R2L mean accuracy |
| --- | ---: | ---: |
| Learner-selected | 77.37% | 78.90% |
| Manually imposed | 77.37% | 79.65% |
| Identity baseline | 85.64% | 85.64% |

Fold-level errors, accuracies, and baseline values corresponding to
dissertation Table 6.14 are in
`results/serbo-croatian-pair-level-summary.tsv`. Feature-projection details are
in the two longer `serbo-croatian-fixed-spec-5fold-*` tables.

Run the learner-selected condition:

```bash
python experiments/run_serbo_croatian_cv.py --spec-set final \
  --output results/serbo-croatian-fixed-spec-cv.tsv
```

The experiment follows the original first-occurrence projection convention:
duplicate pairs created by projecting full bundles onto one feature
specification are evaluated once.

## Polish CHILDES incremental evaluation

The Polish dataset contains 5,003 frequency-ordered pairs: 4,872 identity and
131 non-identity mappings. Ten strict identity-stratified folds use seed 13.
The fixed R2L PRD-SEAL condition stops when all 25 feature mappings and
all held-out pairs are correct.

With batch size 10, success required between 110 and 2,210 training pairs
(mean 922; median 975) and between 2 and 51 non-identity pairs. The exact
success points for batch sizes 10 and 100, corresponding to dissertation Table
6.16, are in `results/polish-childes-success-summary.tsv`.

Detailed files are provided for both batch sizes:

- `*-kfold-summary-*-learning-curve-run.tsv`: fold success points;
- `*-learning-curve-batch-*.tsv`: every evaluated checkpoint;
- `*-aggregate.tsv`: checkpoint means and sample standard deviations;
- `*-failed-pair-counts.tsv`: error counts by fold and checkpoint.

Run either condition and compare every generated checkpoint with its preserved
reference table:

```bash
python experiments/run_polish_childes_cv.py --batch-size 10 --verify-reference
python experiments/run_polish_childes_cv.py --batch-size 100 --verify-reference
```

## Transition-level generalization

Chapter 6 compares each recomposed learned transducer with its corresponding
gold transducer. The reported transition-level agreement is:

| Language and feature condition | L2R match | R2L match |
| --- | ---: | ---: |
| Koasati | 87% | 96% |
| Kerewe | 95% | 87% |
| Samoan | 60% | 69% |
| Lumasaaba | 14% | 14% |
| Lumasaaba, imposed Φ | 68% | 29% |
| Serbo-Croatian | 4% | 16% |
| Serbo-Croatian, imposed Φ | 6% | 36% |

The gold-transition inventory is in
`results/transition-level/table-6.2-gold-transitions.tsv`; the agreement counts
and percentages are in
`results/transition-level/table-6.3-transition-agreement.tsv`. The complete
matched-transition logs, grouped tables, and unattested-context tables are
preserved under `results/transition-level/`.

## Out-of-vocabulary evaluation

The manually constructed Chapter 6 probes are transcribed into
`results/oov/chapter6-oov.tsv`, with a compact condition-level table in
`results/oov/chapter6-oov-summary.tsv`.

| Language and feature condition | L2R correct | R2L correct |
| --- | ---: | ---: |
| Koasati | 9/10 | 10/10 |
| Kerewe | 10/10 | 9/10 |
| Samoan | 10/10 | 10/10 |
| Serbo-Croatian | 8/10 | 9/10 |
| Serbo-Croatian, imposed Φ | 10/10 | 9/10 |

Lumasaaba has no item-level OOV table because its learned transducer did not
support reliable predictions outside the observed sample.

## Verification status

- The five-language full-sample runner completed and matched all ten recorded
  direction-level success counts.
- The corrected Serbo-Croatian learner-selected rerun matched all ten reported
  fold/direction pair-level totals.
- Polish batch-size-10 fold 2 was rerun through its success point at 110 pairs
  with reference verification enabled. A longer replay matched every generated
  checkpoint through folds 1–5 and fold 6 at sample 670 before being stopped;
  the complete preserved ten-fold tables remain included.
- The transition-level summaries are accompanied by the complete saved match
  logs, grouped transition tables, and context-attestation tables.
- The reported Chapter 6 OOV inputs and outputs are preserved in item-level and
  condition-level TSV tables.
- Compilation, package installation, structured-documentation checks, and
  fixed runs with both PRD-SEAL and LCD-SEAL pass. The PRD-SEAL and LCD-SEAL
  inference bodies remain structurally equivalent to the dissertation source
  after documentation and public function names are removed from the
  comparison.
