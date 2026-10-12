# Out-of-vocabulary results

`chapter6-oov.tsv` records the manually constructed test items and SEAL outputs
reported in Chapter 6, Section 6.6.1 of the dissertation. The expanded rows for
the Serbo-Croatian imposed-Φ condition reproduce the checkmarks and alternate
outputs in the published table. An empty `reported_output` with `result` set to
`failed` represents the cross shown in the dissertation.

`chapter6-oov-summary.tsv` gives the corresponding counts by language,
direction, and feature condition. The dissertation does not provide an
item-level Lumasaaba table because its learned transducer did not support
reliable predictions outside the observed sample.
