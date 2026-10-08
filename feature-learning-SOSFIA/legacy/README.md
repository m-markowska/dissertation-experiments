# Legacy experiment scripts

These files are preserved from the public repository because they document the
manual workflow used for the original experiments. They are not supported
entry points:

- `feat_test.py` hard-codes the English configuration and was manually edited
  for other languages and conditions.
- `seg_test.py` contains stale class imports, undefined variables, and a
  mismatched call signature.

They remain useful evidence while the matrix-driven experiment runner is being
reconstructed. New results must use the supported commands under
`experiments/` and should be captured with `tools/capture_run.py`.
