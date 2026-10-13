"""Infer conservative tier content with PFEr and CanTIERr-2.

The implementation follows Algorithms 9 and 10 of Chapter 7. The public entry
points are :func:`cantier_r2` and :func:`convert_backpairs`.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Hashable, Iterable, List, Optional, Sequence, Set, Tuple

Sym = Hashable
OutSym = Hashable
InputStr = Tuple[Sym, ...]
OutputStr = Tuple[OutSym, ...]
RawExample = List[Any]

def _fmt_sym(s: Any) -> str:
    """Render one tier symbol for diagnostic output.

    Args:
        s: Tier symbol to render.

    Returns:
        The symbol's printable value. Singleton tuples are unwrapped.
    """

    if isinstance(s, tuple) and len(s) == 1:
        return str(s[0])
    return str(s)


def fmt_str(w: Sequence[Any]) -> str:
    """Render a sequence of tier symbols as a compact string.

    Args:
        w: Symbol sequence to render.

    Returns:
        Concatenated printable symbol values without separators.
    """
    return "".join(_fmt_sym(a) for a in w)


def fmt_tuple(w: Sequence[Any]) -> str:
    """Render a sequence of tier symbols in tuple notation.

    Args:
        w: Symbol sequence to render.

    Returns:
        Parenthesized, comma-separated printable symbol values.
    """
    return "(" + ", ".join(_fmt_sym(a) for a in w) + ")"


def banner(title: str) -> None:
    """Print a major diagnostic heading.

    Args:
        title: Heading text to print.

    Returns:
        None.
    """
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def subbanner(title: str) -> None:
    """Print a minor diagnostic heading.

    Args:
        title: Heading text to print.

    Returns:
        None.
    """
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def lcp(seqs: Iterable[Sequence[Any]]) -> Tuple[Any, ...]:
    """Compute the longest common prefix of the supplied sequences.

    Args:
        seqs: Sequences to compare.

    Returns:
        Their longest shared prefix, or the empty tuple for no sequences.
    """
    seqs = list(seqs)
    if not seqs:
        return ()
    min_len = min(len(s) for s in seqs)
    out: List[Any] = []
    for i in range(min_len):
        first = seqs[0][i]
        if all(s[i] == first for s in seqs[1:]):
            out.append(first)
        else:
            break
    return tuple(out)


def is_prefix(p: Sequence[Any], w: Sequence[Any]) -> bool:
    """Test whether one symbol sequence prefixes another.

    Args:
        p: Candidate prefix sequence.
        w: Sequence to test.

    Returns:
        ``True`` when ``p`` is a prefix of ``w``.
    """
    p = tuple(p)
    w = tuple(w)
    return len(p) <= len(w) and w[:len(p)] == p


def strip_boundaries_word(
    w: Sequence[Sym],
    left_boundary: Optional[Sym] = None,
    right_boundary: Optional[Sym] = None,
    strip_left: bool = True,
    strip_right: bool = True,
) -> InputStr:
    """Remove configured boundary symbols from an input word.

    Args:
        w: Input symbol sequence.
        left_boundary: Optional left boundary symbol.
        right_boundary: Optional right boundary symbol.
        strip_left: Whether to remove a matching first symbol.
        strip_right: Whether to remove a matching final symbol.

    Returns:
        An immutable input sequence with the requested boundaries removed.
    """
    w = list(w)
    if strip_left and left_boundary is not None and w and w[0] == left_boundary:
        w = w[1:]
    if strip_right and right_boundary is not None and w and w[-1] == right_boundary:
        w = w[:-1]
    return tuple(w)


def alphabet_from_sample(sample: Sequence[Tuple[InputStr, OutputStr]]) -> Set[Sym]:
    """Collect the input alphabet observed in a tier-learning sample.

    Args:
        sample: Tier-learning input-output pairs.

    Returns:
        The distinct symbols occurring in the sample inputs.
    """
    Sigma: Set[Sym] = set()
    for w, _ in sample:
        Sigma.update(w)
    return Sigma


def remove_prefix(prefix: Sequence[Any], seq: Sequence[Any]) -> Tuple[Any, ...]:
    """Remove a required prefix from an output sequence.

    Args:
        prefix: Prefix expected at the start of ``seq``.
        seq: Output sequence from which to remove the prefix.

    Returns:
        The residual suffix, or an empty tuple if the prefix does not match.
    """
    p = tuple(prefix)
    s = tuple(seq)
    if s[:len(p)] != p:
        return ()
    return tuple(s[len(p):])


def suff1_on_tier(w: Sequence[Sym], Theta: Set[Sym]) -> Optional[Sym]:
    """Return the most recent salient symbol under a tier hypothesis.

    Args:
        w: Input prefix to inspect from right to left.
        Theta: Current candidate tier alphabet.

    Returns:
        The rightmost symbol in ``w`` that belongs to ``Theta``, if one exists.
    """
    for a in reversed(tuple(w)):
        if a in Theta:
            return a
    return None


def double_witness_inconsistency(pairs: Sequence[Tuple[InputStr, OutputStr]], debug: bool = False) -> bool:
    """Detect incompatible contributions in two distinct input contexts.

    Args:
        pairs: Context and residual-output observations.
        debug: Whether to print the conflicting witness pair.

    Returns:
        ``True`` iff two distinct contexts have distinct residual outputs.
    """
    if len(pairs) < 2:
        return False

    contrib_to_contexts: Dict[OutputStr, Set[InputStr]] = {}
    for y, r in pairs:
        contrib_to_contexts.setdefault(r, set()).add(y)

    if len(contrib_to_contexts) < 2:
        return False

    contribs = list(contrib_to_contexts.items())
    for i in range(len(contribs)):
        r1, ys1 = contribs[i]
        for j in range(i + 1, len(contribs)):
            r2, ys2 = contribs[j]
            if any(y1 != y2 for y1 in ys1 for y2 in ys2):
                if debug:
                    print("  [double-witness] FOUND")
                    print(f"    r1={fmt_str(r1)}  contexts={[fmt_tuple(y) for y in ys1]}")
                    print(f"    r2={fmt_str(r2)}  contexts={[fmt_tuple(y) for y in ys2]}")
                return True
    return False


def pfe_r(
    sample: Sequence[Tuple[InputStr, OutputStr]],
    Sigma: Optional[Set[Sym]] = None,
    cap_to_input_prefix_len: bool = False,
    debug: bool = False,
) -> Dict[InputStr, OutputStr]:
    """Estimate the prefix function using attested internal prefixes.

    Args:
        sample: Tier-learning input-output pairs.
        Sigma: Input alphabet; inferred from ``sample`` when omitted.
        cap_to_input_prefix_len: Whether to cap each estimated output prefix
            at the corresponding input-prefix length.
        debug: Whether to print prefixes, extensions, and LCP calculations.

    Returns:
        A mapping from each attested internal input prefix to the longest
        common prefix of its compatible sample outputs.
    """
    if Sigma is None:
        Sigma = alphabet_from_sample(sample)

    if debug:
        banner("PFEr: START")
        print(f"Sigma size={len(Sigma)}  Sigma={{{', '.join(_fmt_sym(s) for s in sorted(Sigma, key=str))}}}")

        print("\nSample (w -> u):")
        for w, u in sample:
            print(f"  {fmt_tuple(w)}  ->  {fmt_str(u)}")

    # X = all prefixes of observed words
    X: Set[InputStr] = set()
    for w, _ in sample:
        max_i = len(w)
        if cap_to_input_prefix_len:
            max_i = len(w)  
        for i in range(max_i + 1):
            X.add(w[:i])

    if debug:
        print("\nX = all prefixes of observed words (including empty):")
        for x in sorted(X, key=lambda t: (len(t), str(t))):
            print(f"  |x|={len(x)}  x={fmt_tuple(x)}")

    # Y = internal prefixes: those having at least one 1-symbol extension in X
    Y: Set[InputStr] = set()
    for x in X:
        for a in Sigma:
            if x + (a,) in X:
                Y.add(x)
                break

    if debug:
        print("\nY = internal prefixes (have some 1-symbol extension in X):")
        for y in sorted(Y, key=lambda t: (len(t), str(t))):
            exts = [a for a in Sigma if y + (a,) in X]
            exts_sorted = sorted(exts, key=str)
            print(f"  y={fmt_tuple(y)}  exts={[_fmt_sym(e) for e in exts_sorted]}")

    # P[y] = lcp(outputs of words having prefix y)
    P: Dict[InputStr, OutputStr] = {}
    for y in sorted(Y, key=lambda t: (len(t), str(t))):
        outs = [u for (w, u) in sample if is_prefix(y, w)]
        z = tuple(lcp(outs))


        if cap_to_input_prefix_len:
            z = z[:len(y)]

        P[y] = z

        if debug:
            print("\n--- PFEr entry ---")
            print(f"y = {fmt_tuple(y)}")
            print("Words w with prefix y and their outputs u:")
            for (w, u) in sample:
                if is_prefix(y, w):
                    print(f"  w={fmt_tuple(w)}  u={fmt_str(u)}")
            print("Collected outs:")
            for o in outs:
                print(f"  {fmt_str(o)}")
            print(f"LCP(outs) = z = {fmt_str(z)}")
            print(f"Thus P[y] = {fmt_str(P[y])}")

    if debug:
        banner("PFEr: END")
        print(f"|P|={len(P)} keys (y):")
        for y in sorted(P.keys(), key=lambda t: (len(t), str(t))):
            print(f"  y={fmt_tuple(y)}  P[y]={fmt_str(P[y])}")

    return P


def match(P: Dict[InputStr, OutputStr], Theta: Set[Sym], theta: Sym, debug: bool = False) -> List[Tuple[InputStr, OutputStr]]:
    """Select prefix-function entries whose tier suffix is ``theta``.

    Args:
        P: Prefix-output table computed by :func:`pfe_r`.
        Theta: Current candidate tier alphabet.
        theta: Tier symbol whose matching prefixes are required.
        debug: Whether to print the selected entries.

    Returns:
        Prefix and estimated-output pairs ending in ``theta`` on the tier.
    """
    out: List[Tuple[InputStr, OutputStr]] = []
    for y, z in P.items():
        if suff1_on_tier(y, Theta) == theta:
            out.append((y, z))

    if debug:
        print(f"\nMatch(P, Theta, theta={_fmt_sym(theta)}):")
        if not out:
            print("  (empty)")
        else:
            for y, z in sorted(out, key=lambda yz: (len(yz[0]), str(yz[0]))):
                print(f"  y={fmt_tuple(y)}  z={fmt_str(z)}  suff1_Theta(y)={_fmt_sym(theta)}")

    return out


@dataclass(frozen=True)
class CanTierResult:
    """CanTIERr-2 output containing the tier, alphabet, and PFEr table."""

    theta: Set[Sym]
    Sigma: Set[Sym]
    P: Dict[InputStr, OutputStr]


def cantier_r2(
    sample: Sequence[Tuple[InputStr, OutputStr]],
    Sigma: Optional[Set[Sym]] = None,
    verbose: bool = False,
) -> CanTierResult:
    """Infer conservative tier content from a 2-ITSL sample.

    Args:
        sample: Tier-learning input-output sample.
        Sigma: Input alphabet; inferred from ``sample`` when omitted.
        verbose: Whether to print detailed progress diagnostics.

    Returns:
        The conservative tier, observed alphabet, and prefix-output table.
    """



    if Sigma is None:
        Sigma = alphabet_from_sample(sample)

    RIGHT_BOUNDARY = ('>',)
    Theta: Set[Sym] = set(Sigma) - {RIGHT_BOUNDARY}

    # Optional diagnostics expose the intermediate PFEr and elimination steps.
    if verbose:
        banner("CanTIERr-2: START")
        print(f"Sigma={{{', '.join(_fmt_sym(s) for s in sorted(Sigma, key=str))}}}")
        print(f"|sample|={len(sample)}")
        print("Building PFEr... (cap_to_input_prefix_len=True)")

    P = pfe_r(sample, Sigma=Sigma, cap_to_input_prefix_len=True)

    if verbose:
        print(f"PFEr done. |P|={len(P)}")

    sample_map: Dict[InputStr, OutputStr] = {w: u for (w, u) in sample}

    # Theta: Set[Sym] = set(Sigma)
    RIGHT_BOUNDARY = ('>',)  

    Theta: Set[Sym] = set(Sigma) - {RIGHT_BOUNDARY}

    # ext[y] = {sigma | y+sigma in P}
    ext: Dict[InputStr, Set[Sym]] = {}
    for y_sigma in P.keys():
        if len(y_sigma) == 0:
            continue
        y = y_sigma[:-1]
        sigma = y_sigma[-1]
        ext.setdefault(y, set()).add(sigma)
    # Build X = all prefixes of observed words
    # X: Set[InputStr] = set()
    # for w, _u in sample:
    #     for i in range(len(w) + 1):
    #         X.add(w[:i])

    # # ext[y] = {sigma | y+sigma is an attested prefix in X}
    # ext: Dict[InputStr, Set[Sym]] = {}
    # for y_sigma in X:
    #     if len(y_sigma) == 0:
    #         continue
    #     y = y_sigma[:-1]
    #     sigma = y_sigma[-1]
    #     ext.setdefault(y, set()).add(sigma)

    if verbose:
        subbanner("Precomputed ext[y] = {sigma | y+sigma in P}")
        print(f"|ext|={len(ext)}")
        # show a compact sample of ext entries (avoid flooding)
        shown = 0
        for y in sorted(ext.keys(), key=lambda t: (len(t), str(t))):
            sigs = sorted(ext[y], key=str)
            print(f"  y={fmt_tuple(y):<35}  sigmas={[_fmt_sym(s) for s in sigs]}")
            shown += 1
            if shown >= 25 and len(ext) > 25:
                print("  ...")
                break

    remove: Set[Sym] = {next(iter(Sigma))} if Sigma else set()
    it = 0

    while remove:
        it += 1
        remove = set()

        if verbose:
            banner(f"ITERATION {it}")
            print(f"Current Theta={{{', '.join(_fmt_sym(t) for t in sorted(Theta, key=str))}}}")

        for theta in list(Theta):

            if verbose:
                subbanner(f"Testing theta = {_fmt_sym(theta)}")

            Match = match(P, Theta, theta)

            if verbose:
                print(f"Match size = {len(Match)}")
                if len(Match) <= 15:
                    for y, z in sorted(Match, key=lambda yz: (len(yz[0]), str(yz[0]))):
                        print(f"  y={fmt_tuple(y):<35}  z={fmt_str(z)}")
                elif len(Match) > 0:
                    # show a few examples
                    for y, z in sorted(Match, key=lambda yz: (len(yz[0]), str(yz[0])))[:10]:
                        print(f"  y={fmt_tuple(y):<35}  z={fmt_str(z)}")
                    print("  ...")

            # Next(theta): attested continuations
            Next: Set[Sym] = set()
            for y, _z in Match:
                Next.update(ext.get(y, set()))

            if verbose:
                print(f"Next(theta={_fmt_sym(theta)}) = {{{', '.join(_fmt_sym(s) for s in sorted(Next, key=str))}}}")

            removed_now = False

            # ---- main W_{theta,sigma} checks ----
            for sigma in Next:
                if verbose:
                    print("\n  " + "." * 70)
                    print(f"  Checking sigma = {_fmt_sym(sigma)} for theta={_fmt_sym(theta)}")

                W: List[Tuple[InputStr, OutputStr]] = []

                for y, z in Match:
                    y_sigma = y + (sigma,)


                    y_sigma = y + (sigma,)
                    if y_sigma not in P:
                        if verbose:
                            print(f"    (skip) y={fmt_tuple(y)} because y+sigma not in P")
                        continue

                    x = P[y_sigma]

                    # FULL residual (can be longer)
                    r_full = remove_prefix(z, x)

                    # RESTRICTED residual: take only first symbol
                    r = r_full[:1]

                    W.append((y, r))

                    if verbose:
                        print(f"    y={fmt_tuple(y)}")
                        print(f"      z=P[y]         = {fmt_str(z)}")
                        print(f"      y+sigma        = {fmt_tuple(y_sigma)}")
                        print(f"      x=P[y+sigma]   = {fmt_str(x)}")
                        print(f"      r_full=z^-1·x  = {fmt_str(r_full)}")
                        print(f"      r_1            = {fmt_str(r)}")

                if verbose:
                    print(f"  Built W with {len(W)} witnesses (restricted to 1).")
                    print("  Final W list (restricted to 1):")
                    for yy, rr in W:
                        print(f"    (y={fmt_tuple(yy)}, r_1={fmt_str(rr)})")


                if double_witness_inconsistency(W):
                    if verbose:
                        print(f"  ==> REMOVE theta={_fmt_sym(theta)} (double-witness inconsistency in W_{_fmt_sym(theta)},{_fmt_sym(sigma)})")
                    remove.add(theta)
                    removed_now = True
                    break
                else:
                    if verbose:
                        print("  ==> consistent (no removal from this sigma)")

            # ---- word-final W_end checks ----
            if not removed_now:

                if verbose:
                    print("\n  " + "." * 70)
                    print(f"  Checking word-final W_end for theta={_fmt_sym(theta)}")

                W_end: List[Tuple[InputStr, OutputStr]] = []

                for y, z in Match:
                    if y not in sample_map:

                        if verbose:
                            print(f"    (skip END) y={fmt_tuple(y)} not a full word in sample")
                        continue

                    u = sample_map[y]

                    r_full = remove_prefix(z, u)
                    r = r_full[:1]

                    W_end.append((y, r))

                    if verbose:
                        print(f"    [END] y={fmt_tuple(y)}")
                        print(f"      z=P[y]         = {fmt_str(z)}")
                        print(f"      u=sample[y]    = {fmt_str(u)}")
                        print(f"      r_full=z^-1·u  = {fmt_str(r_full)}")
                        print(f"      r_1            = {fmt_str(r)}")

                if verbose:
                    print(f"  Built W_end with {len(W_end)} witnesses (restricted to 1).")
                    print("  Final W_end list (restricted to 1):")
                    for yy, rr in W_end:
                        print(f"    (y={fmt_tuple(yy)}, r_1={fmt_str(rr)})")

                if double_witness_inconsistency(W_end):
                    if verbose:
                        print(f"  ==> REMOVE theta={_fmt_sym(theta)} (double-witness inconsistency in W_end,{_fmt_sym(theta)})")
                    remove.add(theta)
                else:
                    if verbose:
                        print("  ==> consistent (no removal from word-final check)")

        Theta = Theta - remove

        if verbose:
            banner(f"ITERATION {it} SUMMARY")
            print(f"Removed this iter: {{{', '.join(_fmt_sym(t) for t in sorted(remove, key=str))}}}")
            print(f"New Theta:         {{{', '.join(_fmt_sym(t) for t in sorted(Theta, key=str))}}}")
            print(f"[iter {it}] removed={remove}  Theta={Theta}")

    if verbose:
        banner("CanTIERr-2: END")
        print(f"Final Theta={{{', '.join(_fmt_sym(t) for t in sorted(Theta, key=str))}}}")

    return CanTierResult(theta=Theta, Sigma=set(Sigma), P=P)


def convert_backpairs(
    raw: Sequence[RawExample],
    left_boundary: Optional[Sym] = ('<',),
    right_boundary: Optional[Sym] = ('>',),
    strip_left: bool = True,
    strip_right: bool = True,
) -> List[Tuple[InputStr, OutputStr]]:
    """Convert boundary-marked project data to CanTIERr pair tuples.

    Args:
        raw: Boundary-marked raw pairs.
        left_boundary: Optional left boundary symbol.
        right_boundary: Optional right boundary symbol.
        strip_left: Whether to remove the left boundary symbol.
        strip_right: Whether to remove the right boundary symbol.

    Returns:
        Normalized input and output tuple pairs.
    """
    out: List[Tuple[InputStr, OutputStr]] = []
    for item in raw:
        inp_list, out_str = item
        w = strip_boundaries_word(
            inp_list,
            left_boundary=left_boundary,
            right_boundary=right_boundary,
            strip_left=strip_left,
            strip_right=strip_right,
        )
        u = tuple(out_str)  # string -> tuple of chars
        out.append((w, u))
    return out
