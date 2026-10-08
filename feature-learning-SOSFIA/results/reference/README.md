# Appendix B reference results

These TSV files are a machine-readable transcription of the final results in
Appendix B of Magdalena Markowska's dissertation. The dissertation is the
authoritative source. These values document the historical experiments; they
must not be replaced by numbers from later reproducibility runs.

Source artifact: *Learning Phonological Transductions from Sparse Data over
Structured Representations* (Stony Brook University, 2026), PDF SHA-256
`89113278c51e12add10d1c28e5ea4e570d8b19a38c183b6d26874d362549fca0`.

Included SOSFIA and FxF(SOSFIA) tables:

- English: B.1–B.8
- Yawelmani: B.13–B.20
- Chukchi: B.25–B.32
- Polish: B.37–B.48

Appendix tables B.9–B.12, B.21–B.24, B.33–B.36, and B.49–B.52 report SEAL
experiments and are intentionally excluded because they belong with the
equational-learner release rather than this SOSFIA repository.

Files:

- `appendix_b_runs.tsv` transcribes the ten individual selected-sample
  cardinalities in each raw-results table. `M_phi` is a feature-specific sample
  and `M_F` is the synthesized sample shown as `MF` in the dissertation.
- `appendix_b_summaries.tsv` transcribes the full sample size, reported mean,
  and reported sample standard deviation for each feature. Its
  `source_runs_table_id` links each summary to its ten individual runs. A
  non-empty `validation_note` records a printed summary that does not match the
  values in its linked raw table; neither published value is silently changed.
- `appendix_b_polish_alphabet_growth.tsv` transcribes the single-run Polish
  comparisons for alphabet sizes 8, 9, and 10.

Feature bundles split across multiple lines in the typeset tables are written
with `+`, for example `nasal+cons`. The synthesized row is named
`__synthesized__`. Thousands separators are omitted so numeric fields can be
read directly as numbers. `dissertation_page` is the printed page number.

The files were produced with `tools/extract_appendix_b.py` from Ghostscript
`txtwrite` output. During extraction, every reported mean and SD is checked
against its corresponding ten-run table and any discrepancy is recorded. The
dissertation itself is not distributed in this repository.
