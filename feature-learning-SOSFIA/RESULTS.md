# Results and reproducibility status

The historical minimal-sample experiments printed their results to the
terminal. The final values were copied manually into the associated paper and
dissertation, but the complete terminal logs, random seeds, and
machine-readable result files were not retained. The dissertation's Appendix B
preserves the final per-feature cardinalities for the ten runs, so these values
are the authoritative final results. The original random draws cannot be
replayed exactly because their seeds were not recorded; this limits exact
replay of the computation, not the status of the dissertation results.

This does not invalidate the included implementation or data. All stored
feature-pair tables can be regenerated exactly from the stored segment pairs
and inventories with `python experiments/verify_data.py`. New experimental runs
should be launched through `tools/capture_run.py`, which saves the command,
seed, Git commit, environment, elapsed time, exit status, and combined terminal
output under `results/runs/`.

The numbers reported in the dissertation are final and must not be recalculated
or replaced in this repository. Any future seeded run is a reproducibility
check only. Store its output separately, label it as a new run, and compare it
with the dissertation without changing the authoritative values.

The SOSFIA and FxF(SOSFIA) tables from Appendix B are transcribed under
`results/reference/` as TSV files. They include the individual historical run
values, the published summaries, and the Polish alphabet-growth results.

`experiments/EXPERIMENT_MATRIX.tsv` inventories the SOSFIA conditions described
in Chapters 3 and 4 and Appendix B. Its seed schedules apply only to optional
new reproducibility checks, not to the unknown historical seeds.

## Recording a new run

For example:

```bash
python tools/capture_run.py \
  --name english-minimal-sample \
  --seed 13 \
  -- python path/to/experiment.py
```

The seed is exposed to Python processes as `FXF_SOSFIA_SEED` and
`PYTHONHASHSEED`. Importing `fxf_sosfia.sample_search` applies it to Python's
`random` module and NumPy's random generator.

Commit compact result summaries and metadata needed to support reported
claims. Large exploratory logs may be archived separately, with their checksum
and location recorded here.
