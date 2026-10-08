# Experiment inventory

`EXPERIMENT_MATRIX.tsv` is a reconstruction of the FxF(SOSFIA)
conditions reported in dissertation Chapters 3 and 4 and Appendix B. It
separates the four main language conditions, processing direction, fixed versus
learned locality, and the Polish alphabet-growth conditions.

As currently reconstructed, the matrix contains 32 conditions and 212 possible
verification-run instances. These are not required to establish or replace the
final results reported in the dissertation. Several conditions can take hours,
so any optional verification should be estimated from pilots rather than run as
one monolithic command.

`feat_test.py` provides the feature-learning driver. Complete matrix reruns are
optional and can take several hours; the dissertation tables remain the final
reported results.

The proposed seeds `1-10` are for optional new reproducibility checks. They are
not claims about the seeds used for the final dissertation results, which were
not saved.

## Sampling

The dissertation presents AMßA as adding 10 randomly selected pairs per
iteration. The preserved implementation is more specific: it alternates
identity and non-identity examples. The feature driver accepts `--batch-size`
so a new run records the selected sampling schedule explicitly.

SEAL conditions in Appendix B are intentionally excluded from this SOSFIA
matrix; they belong in the equational-learner reproducibility workflow.
