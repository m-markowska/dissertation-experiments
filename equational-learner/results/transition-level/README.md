# Transition-level results

The summary tables reproduce the transition analyses reported in Chapter 6,
Section 6.6.1 of the dissertation:

- `table-6.2-gold-transitions.tsv` records the gold-transducer transition
  inventory and its identity/non-identity composition.
- `table-6.3-transition-agreement.tsv` records agreement between the
  recomposed learned transducers and the gold transducers.

The supporting artifacts are organized as follows:

- `raw-matches/`: complete matched-transition comparison logs;
- `grouped-matches/`: matched transitions grouped into CSV tables;
- `unattested-contexts/`: matched transitions whose corresponding contexts
  are unattested in the observed dataset.

Rows with `manually_imposed` feature conditions correspond to the imposed-Φ
conditions reported for Lumasaaba and Serbo-Croatian.
