# Result-file index

Start with `../RESULTS.md` for the experimental design and headline findings.

## Compact summaries

- `textbook-full-sample-summary.tsv`: success counts for five languages and two
  directions.
- `serbo-croatian-pair-level-summary.tsv`: dissertation Table 6.14 in tidy TSV
  form.
- `polish-childes-success-summary.tsv`: dissertation Table 6.16 in tidy TSV
  form.
- `transition-level/table-6.2-gold-transitions.tsv`: gold-transition counts
  from dissertation Table 6.2.
- `transition-level/table-6.3-transition-agreement.tsv`: learned/gold
  transition agreement from dissertation Table 6.3.
- `oov/chapter6-oov-summary.tsv`: accuracy on the manually constructed
  Chapter 6 OOV probes.

## Detailed reference outputs

- `textbook-full-sample.tsv`: all 250 full-sample feature/direction runs.
- `serbo-croatian-fixed-spec-5fold-summary-dsf-seed-13-random-order.tsv`:
  feature-level Serbo-Croatian results.
- `serbo-croatian-fixed-spec-5fold-summary-dsf-seed-13-random-order-fold-accuracy.tsv`:
  aggregated feature-projection results and identity baseline.
- `pol-5000-*-batch-10-*`: Polish incremental checkpoints at intervals of 10.
- `pol-5000-*-batch-100-*`: Polish incremental checkpoints at intervals of 100.
- `transition-level/raw-matches/`: complete matched-transition logs.
- `transition-level/grouped-matches/`: matched transitions in CSV form.
- `transition-level/unattested-contexts/`: context-attestation diagnostics.
- `oov/chapter6-oov.tsv`: item-level inputs and reported outputs for the OOV
  evaluation.

The detailed files are preserved experiment outputs. Rerun commands write to
separate filenames or directories so the references are not silently replaced.
The strings `dsf` and `identity` in preserved historical filenames are legacy
implementation labels: they correspond to LCD-SEAL and PRD-SEAL,
respectively. Identity *pairs* and the identity evaluation baseline are data
properties, not names for a SEAL mode.
