"""Implement the PRD-SEAL and LCD-SEAL output-distribution modes.

Both modes infer the global placeholder mapping described in Chapter 5 of the
dissertation. PRD-SEAL resolves conflicts by pushing output material to the
right; LCD-SEAL searches length-constrained placeholder domains. Their
historical implementations are preserved in this module.
"""

from __future__ import annotations
from copy import deepcopy
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple



def _align_1to1(middle: List[str], out_tokens: List[str]) -> List[str]:
    """Align output tokens one-to-one with an input-symbol sequence.

    Args:
        middle: Input symbols whose positions require output assignments.
        out_tokens: Output tokens to align.

    Returns:
        A list as long as ``middle``. Short outputs are padded with epsilon;
        excess outputs are concatenated into the final position.
    """
    Lm, Lo = len(middle), len(out_tokens)
    # print('Lm: ', Lm)
    # print('Lo: ', Lo)
    # print('out_tokens: ', out_tokens)
    if Lm == Lo:
        return out_tokens[:]
    elif Lm < Lo:
        head = out_tokens[:Lm-1]
        tail = ["".join(out_tokens[Lm-1:])] if Lm > 0 else ["".join(out_tokens)]
        return head + tail
    else:
        return out_tokens + [""] * (Lm - Lo)


def buildH(rows: Iterable[Tuple[str, Sequence[str], Sequence[str]]]) -> Dict[str, Set[str]]:
    """Collect observed output strings for each input symbol.

    Args:
        rows: Triples containing a left edge, input symbols, and aligned outputs.

    Returns:
        Mapping from each symbol to its observed output strings; left edges map
        to epsilon.
    """
    H = defaultdict(set)
    for left, middle, aligned in rows:
        H[left].add('')  # O1 -> {''}
        for seg, tok in zip(middle, aligned):
            H[seg].add(tok)
    return dict(H)


def compare_H(identH: Dict[str, object], predictedH: Dict[str, object]) -> Dict[str, object]:
    """Update shared keys in an existing hypothesis with predicted values.

    Args:
        identH: Baseline hypothesis modified in place.
        predictedH: Newly inferred values keyed by encoded symbol.

    Returns:
        The updated ``identH`` dictionary.
    """

    for k,v in predictedH.items():
        if k in identH.keys():
            if identH[k] != v:
                identH[k] = v

    # return predictedH
    return identH


def lcp(strings: Iterable[str]) -> str:
    """Find the longest prefix common to all supplied strings.

    Args:
        strings: Strings whose shared prefix is required.

    Returns:
        The longest common prefix, or the empty string for empty input.
    """
    strings = list(strings)
    if not strings:
        return ""
    s1, s2 = min(strings), max(strings)
    i = 0
    while i < len(s1) and i < len(s2) and s1[i] == s2[i]:
        i += 1
    return s1[:i]


def learn_prd_seal(
    data: List[Tuple[List[str], str]],
    #delta_path: str,
    identH: dict,
) -> Dict[str, str]:
    """Infer output assignments with PRD-SEAL.

    The learner aligns outputs to encoded symbols, identifies symbols with
    conflicting values, retains their longest common prefix, and pushes each
    remainder one position to the right until no further conflict is resolved.

    Args:
        data: Encoded input/output training examples.
        identH: Baseline identity hypothesis updated with inferred assignments.

    Returns:
        The updated hypothesis mapping symbols to output values.
    """
    # ---------- First pass: tokenize, align, collect per-segment outputs ----------
    per_seg_outputs: Dict[str, set] = {}
    rows = []  # store per-pair info: (left, middle, right, aligned_orig)

    for inp, out_str in data:
        # print(f'inp: {inp} \t out_str: {out_str}')
        # left, right = inp[0], inp[-1]
        left = inp[0]
        # middle = inp[1:-1]
        middle = inp[1:]
        # out_tokens is a List!!!!!
        # out_tokens = _tokenize_segments(out_str, delta_path) #--> use when using IPA
        # aligned = _align_1to1(middle, out_tokens) #--> use when using IPA
        aligned = _align_1to1(middle, list(out_str))
        # print('aligned: ', aligned)

        for seg, tok in zip(middle, aligned):
            per_seg_outputs.setdefault(seg, set()).add(tok)

        # rows.append((left, middle, right, aligned))
        rows.append((left, middle, aligned))
    # print('rows:  ', rows)
    # print('per_seg_outputs:  ')
    # pprint(per_seg_outputs)
    # Conflicts: any middle symbol with >1 distinct tokens across pairs
    conflicts = {seg for seg, outs in per_seg_outputs.items() if len(outs) > 1}
    # print('conflicts:  ', conflicts)

    # base case: no conflicts
    if len(conflicts) == 0:
        return compare_H(identH, buildH(rows))

    # keep changing until there are no conflicts
    while len(conflicts) > 0:
        prev_rows = rows
        prev_conflicts = conflicts.copy()   # <-- ADD THIS

        # print('-------------------------------------------------')
        # print('-------------CONFLICTS---------------------------')
        # print(conflicts)
        # print('-------------------------------------------------')

        lcp_map = {seg: lcp(per_seg_outputs[seg]) for seg in conflicts}
        # pprint(lcp_map)
        adjusted_rows = []
        for left, middle, aligned in rows:
            n = len(middle)
            push_into = [""] * (n + 1)
            clear_here = [False] * n

            for i, seg in enumerate(middle):
                if seg in conflicts:
                    tok = aligned[i]
                    pref = lcp_map[seg]
                    rem  = tok[len(pref):]

                    clear_here[i] = False
                    aligned[i] = pref

                    if rem:
                        if i + 1 < n:
                            push_into[i + 1] += rem
                        else:
                            push_into[i] += rem

            final_tokens = []
            for i in range(n):
                own = "" if clear_here[i] else aligned[i]
                final_tokens.append(push_into[i] + own)
            # if push_into[i] and middle[i] in conflicts:
            #     print("CONFLICT ABSORB:", middle[i], "incoming=", push_into[i], "own=", aligned[i], "=>", push_into[i] + aligned[i])


            adjusted_rows.append((left, middle, final_tokens))

        if adjusted_rows == prev_rows:
            break

        rows = adjusted_rows

        # recompute conflicts for next round
        per_seg_outputs = {}
        for _, middle, aligned in rows:
            for seg, tok in zip(middle, aligned):
                per_seg_outputs.setdefault(seg, set()).add(tok)
        # print('per seg outoputs:')
        # pprint(per_seg_outputs)
        conflicts = {seg for seg, outs in per_seg_outputs.items() if len(outs) > 1}

        if conflicts == prev_conflicts:     # <-- ADD THIS (stop if no conflicts resolved)
            break

    # when loop finishes, no conflicts remain
    return compare_H(identH, buildH(rows))


def value_rank(v: str) -> Tuple[int, int, str]:
    """Build the preference key used to order candidate output strings.

    Args:
        v: Candidate output string.

    Returns:
        Sort key prioritizing one-character strings, then epsilon, then longer
        strings by length and lexicographic order.
    """
    if v != "" and len(v) == 1:
        return (0, 0, v)
    if v == "":
        return (1, 0, v)
    return (2, len(v), v)


def sort_vals(vals: Set[str]) -> List[str]:
    """Sort candidate outputs by the learner's preference order.

    Args:
        vals: Candidate output strings.

    Returns:
        Candidates ordered using :func:`value_rank`.
    """
    return sorted(vals, key=value_rank)


def sym_sort_key(sym: str) -> Tuple[int, str]:
    """Build a numeric-aware ordering key for encoded symbols.

    Args:
        sym: Encoded symbol, normally an ``O`` followed by an integer.

    Returns:
        Numeric suffix and original symbol; unparseable suffixes sort last.
    """
    try:
        return (int(sym[1:]), sym)
    except Exception:
        return (10**9, sym)


def edge_symbols(data: List[Tuple[List[str], str]]) -> Set[str]:
    """Collect first-position symbols that must map to epsilon.

    Args:
        data: Encoded input/output examples.

    Returns:
        First symbols from all nonempty inputs. Final symbols are not included.
    """
    E: Set[str] = set()
    for inp, _ in data:
        if not inp:
            continue
        E.add(inp[0])      # keep: first boundary forced to ''
        # removed: E.add(inp[-1])
    return E


def init_domains_context_aware_with_edges(
    data: List[Tuple[List[str], str]],
    max_len: int,
    alphabet: List[str],
    EDGE: Set[str],
    verbose: bool = False,
) -> Dict[str, Set[str]]:
    """Initialize context-sensitive output domains for encoded symbols.

    Args:
        data: Encoded input/output training examples.
        max_len: Maximum output-string length assigned to one symbol.
        alphabet: Permitted characters in candidate outputs.
        EDGE: Symbols constrained to map to epsilon.
        verbose: Whether to print domain-construction diagnostics.

    Returns:
        Candidate output strings for every symbol occurring in ``data``.

    Raises:
        ValueError: If intersecting example constraints empties a domain.
    """
    syms: Set[str] = set()
    for inp, _ in data:
        syms.update(inp)

    def substrings_starting_in_window(s: str, lo: int, hi: int) -> Set[str]:
        """Enumerate permitted substrings beginning within an index window.

        Args:
            s: Output string from which candidates are drawn.
            lo: Inclusive lower bound for the starting index.
            hi: Inclusive upper bound for the starting index.

        Returns:
            Epsilon and substrings no longer than ``max_len`` whose characters
            belong to the configured output alphabet.
        """
        n = len(s)
        lo = max(0, min(lo, n))
        hi = max(0, min(hi, n))
        cand: Set[str] = set()
        for st in range(lo, hi + 1):
            cand.add("")
            for L in range(1, max_len + 1):
                if st + L <= n:
                    cand.add(s[st:st+L])
        cand = {x for x in cand if all(ch in alphabet for ch in x)}
        return cand

    # Start with None then intersect down
    D: Dict[str, Optional[Set[str]]] = {s: None for s in syms}

    for ex_i, (inp, out_str) in enumerate(data, start=1):
        n = len(out_str)
        k = len(inp)

        # length bounds per token: [0, max_len]
        prefix_min = [0] * (k + 1)
        prefix_max = [0] * (k + 1)
        for i in range(k):
            prefix_min[i+1] = prefix_min[i]
            prefix_max[i+1] = prefix_max[i] + max_len

        for j, sym in enumerate(inp):
            # EDGE symbols are forced to '' regardless of context
            if sym in EDGE:
                cand_here = {""}
            else:
                start_lo = prefix_min[j]
                start_hi = prefix_max[j]
                max_suffix = (k - (j + 1)) * max_len
                start_lo = max(start_lo, n - (max_len + max_suffix))
                start_hi = min(start_hi, n)
                cand_here = substrings_starting_in_window(out_str, start_lo, start_hi)

            if D[sym] is None:
                D[sym] = set(cand_here)
            else:
                D[sym] = D[sym].intersection(cand_here)

        if verbose:
            print(f"[init] processed EX{ex_i}/{len(data)} out='{out_str}'")

    outD: Dict[str, Set[str]] = {}
    for s in syms:
        outD[s] = D[s] if D[s] is not None else {""}

    # Enforce EDGE hard constraint at the end too (safety)
    for s in EDGE:
        outD[s] = {""}

    # Validate no wipeouts
    for s in syms:
        if len(outD[s]) == 0:
            raise ValueError(f"[init] domain wipeout for {s}. Increase max_len or check data.")

    if verbose:
        print("\n[init] EDGE symbols forced to epsilon:")
        print(" ", sorted(EDGE, key=sym_sort_key))
        print("\n[init] preference order used:")
        print("  len=1 first ")
        print("\n[init] initial domains:")
        for s in sorted(outD.keys(), key=sym_sort_key):
            print(f"  {s}: {sort_vals(outD[s])}")

    return outD


def example_satisfiable(
    inp: List[str],
    out_str: str,
    D: Dict[str, Set[str]],
    max_len: int,
    fixed: Optional[Dict[str, str]] = None,
) -> bool:
    """Test whether one example admits a consistent symbol assignment.

    Args:
        inp: Encoded input-symbol sequence.
        out_str: Required concatenated output string.
        D: Candidate output domain for each symbol.
        max_len: Maximum permitted output length for one symbol.
        fixed: Optional symbol assignments held constant during the search.

    Returns:
        True if a consistent assignment concatenates exactly to ``out_str``.
    """
    if fixed is None:
        fixed = {}

    n = len(out_str)

    allowed: Dict[str, List[str]] = {}
    for sym in set(inp):
        if sym not in D:
            return False
        
        if len(D[sym]) == 0:
            return False # 
        
        if sym in fixed:
            v = fixed[sym]
            if v not in D[sym]:
                return False
            allowed[sym] = [v]
        else:
            allowed[sym] = sort_vals(D[sym])

        if len(allowed[sym]) == 0:
            return False

    asn: Dict[str, str] = {}
    failed: Set[Tuple[int, int, Tuple[Tuple[str, str], ...]]] = set()

    def sig() -> Tuple[Tuple[str, str], ...]:
        """Return a hashable signature of current assignments.

        Args:
            None.

        Returns:
            Sorted ``(symbol, value)`` pairs from the current search branch.
        """
        return tuple(sorted(asn.items()))

    def remaining_len_bounds(idx: int) -> Tuple[int, int]:
        """Bound the output length possible from the remaining input.

        Args:
            idx: Index of the next input symbol to process.

        Returns:
            Minimum and maximum lengths admitted by current assignments and
            domains for the suffix beginning at ``idx``.
        """
        lo = 0
        hi = 0
        for j in range(idx, len(inp)):
            s = inp[j]
            if s in asn:
                L = len(asn[s])
                lo += L
                hi += L
            else:
                vals = allowed[s]
                lo += min(len(v) for v in vals)
                hi += max(len(v) for v in vals)
        return lo, hi

    def go(idx: int, pos: int) -> bool:
        """Search assignments for the remaining input and output suffixes.

        Args:
            idx: Index of the next input symbol.
            pos: Index of the next unmatched output character.

        Returns:
            True if the suffixes admit a consistent completion.
        """
        state = (idx, pos, sig())
        if state in failed:
            return False

        if idx == len(inp):
            ok = (pos == n)
            if not ok:
                failed.add(state)
            return ok

        lo, hi = remaining_len_bounds(idx)
        rem = n - pos
        if not (lo <= rem <= hi):
            failed.add(state)
            return False

        sym = inp[idx]

        if sym in asn:
            v = asn[sym]
            L = len(v)
            if out_str[pos:pos+L] != v:
                failed.add(state)
                return False
            return go(idx + 1, pos + L)

        for v in allowed[sym]:
            if len(v) > max_len:
                continue
            L = len(v)
            if out_str[pos:pos+L] != v:
                continue
            asn[sym] = v
            if go(idx + 1, pos + L):
                return True
            del asn[sym]

        failed.add(state)
        return False

    return go(0, 0)


def dataset_satisfiable(
    data: Sequence[Tuple[List[str], str]], D: Dict[str, Set[str]], max_len: int
) -> bool:
    """Test whether every example is satisfiable under current domains.

    Args:
        data: Encoded input/output examples.
        D: Candidate output domain for each encoded symbol.
        max_len: Maximum permitted output length for one symbol.

    Returns:
        True when each example has at least one consistent assignment.
    """
    return all(example_satisfiable(inp, out_str, D, max_len) for inp, out_str in data)


def candidate_consistent_globally(
    sym: str,
    v: str,
    data: Sequence[Tuple[List[str], str]],
    D: Dict[str, Set[str]],
    max_len: int,
) -> bool:
    """Test one symbol value against every example containing that symbol.

    Args:
        sym: Encoded symbol to fix.
        v: Candidate output value for ``sym``.
        data: Encoded input/output examples.
        D: Current candidate domains.
        max_len: Maximum permitted output length for one symbol.

    Returns:
        True if all relevant examples remain satisfiable with ``sym = v``.
    """
    fixed = {sym: v}
    for inp, out_str in data:
        if sym not in inp:
            continue
        if not example_satisfiable(inp, out_str, D, max_len, fixed=fixed):
            return False
    return True


def propagate_by_global_elimination(
    data: List[Tuple[List[str], str]],
    D: Dict[str, Set[str]],
    max_len: int,
    EDGE: Set[str],
    verbose: bool = False,
    do_global: bool = True,          # NEW
    max_rounds: int = 10**9,         # NEW safety cap (optional)
) -> Dict[str, Set[str]]:
    """Prune domain values that make relevant examples unsatisfiable.

    Args:
        data: Encoded input/output examples.
        D: Initial candidate domains.
        max_len: Maximum permitted output length for one symbol.
        EDGE: Symbols constrained to epsilon.
        verbose: Whether to print propagation diagnostics.
        do_global: Whether to perform global consistency pruning.
        max_rounds: Safety limit on propagation rounds.

    Returns:
        A copied and pruned domain mapping. An empty domain records failure.
    """
    D = deepcopy(D)

    # hard enforce EDGE always
    for s in EDGE:
        D[s] = {""}

    # If global pruning is off, propagation is just EDGE enforcement.
    if not do_global:
        return D

    changed = True
    r = 0

    while changed and r < max_rounds:
        r += 1
        changed = False
        if verbose:
            print("\n" + "#" * 90)
            print(f"PROP ROUND {r}: start")
            print("#" * 90)

        for sym in sorted(D.keys(), key=sym_sort_key):
            if sym in EDGE:
                if verbose:
                    print(f"  {sym} (EDGE): ['']")
                continue

            vals = sort_vals(D[sym])
            if verbose:
                print(f"  {sym}: {vals}")

            remove = []
            for v in vals:
                if not candidate_consistent_globally(sym, v, data, D, max_len):
                    remove.append(v)

            if remove:
                if verbose:
                    print(f"    PRUNE {sym}: removing {remove}")
                for v in remove:
                    D[sym].remove(v)
                changed = True
                if len(D[sym]) == 0:
                    if verbose:
                        print(f"    DOMAIN WIPEOUT at {sym}")
                    return D

        if verbose:
            print(f"PROP ROUND {r}: end (changed={changed})")

    # safety
    for s in EDGE:
        D[s] = {""}

    return D


def pick_next_symbol(D: Dict[str, Set[str]], EDGE: Set[str]) -> Optional[str]:
    """Choose the smallest unresolved non-edge domain for branching.

    Args:
        D: Current candidate domains.
        EDGE: Symbols excluded from branching because they map to epsilon.

    Returns:
        Selected symbol, or ``None`` when all non-edge domains are singletons.
    """
    cands = [(len(vs), sym) for sym, vs in D.items() if sym not in EDGE and len(vs) > 1]
    if not cands:
        return None
    cands.sort()
    return cands[0][1]


def solve_to_singletons(
    data: List[Tuple[List[str], str]],
    D0: Dict[str, Set[str]],
    max_len: int,
    EDGE: Set[str],
    verbose: bool = False,
    depth: int = 0,
) -> Optional[Dict[str, Set[str]]]:
    """Resolve all domains with propagation and depth-first search.

    Args:
        data: Encoded input/output examples.
        D0: Candidate domains at the current branch.
        max_len: Maximum permitted output length for one symbol.
        EDGE: Symbols constrained to epsilon.
        verbose: Whether to print search diagnostics.
        depth: Current recursion depth, used for diagnostics.

    Returns:
        Singleton domains satisfying the data, or ``None`` when no assignment
        exists below the current branch.
    """
    indent = "  " * depth

    # Enforce EDGE in this branch
    D0 = deepcopy(D0)
    for s in EDGE:
        D0[s] = {""}

    if verbose:
        amb = {k: sort_vals(v) for k, v in D0.items() if k not in EDGE and len(v) > 1}
        print(f"\n{indent}=== SOLVE depth={depth} ===")
        print(f"{indent}ambiguous (non-EDGE) symbols: {len(amb)}")
        for k in sorted(amb.keys(), key=lambda s: (len(amb[s]), sym_sort_key(s))):
            print(f"{indent}  {k}: {amb[k]}")

    D = propagate_by_global_elimination(data, D0, max_len, EDGE, verbose=verbose)

    for sym, vs in D.items():
        if len(vs) == 0:
            if verbose:
                print(f"{indent}BACKTRACK (wipeout)")
            return None

    nxt = pick_next_symbol(D, EDGE)
    if nxt is None:
        if verbose:
            print(f"{indent}SUCCESS: all singletons (non-EDGE), EDGE fixed to ''")
        return D
    
    if depth % 10 == 0:
        amb = sum(1 for s in D if s not in EDGE and len(D[s]) > 1)
        tot = sum(len(D[s]) for s in D if s not in EDGE)
        # print(f"[prog] depth={depth} amb={amb} total_nonedge_candidates={tot} nxt={nxt} dom={len(D[nxt])}")


    choices = sort_vals(D[nxt])
    if verbose:
        print(f"{indent}BRANCH on {nxt} choices={choices}")

    for v in choices:
        if verbose:
            print(f"{indent}  TRY {nxt} := '{v}'")
        D_branch = deepcopy(D)
        D_branch[nxt] = {v}
        for s in EDGE:
            D_branch[s] = {""}

        if not dataset_satisfiable(data, D_branch, max_len):
            if verbose:
                print(f"{indent}    immediate FAIL (dataset unsat)")
            continue

        sol = solve_to_singletons(data, D_branch, max_len, EDGE, verbose=verbose, depth=depth + 1)
        if sol is not None:
            return sol

        if verbose:
            print(f"{indent}  backtrack from {nxt} := '{v}'")

    if verbose:
        print(f"{indent}NO VALUE WORKED for {nxt} -> BACKTRACK")
    return None


def infer_alphabet_from_data(data: List[Tuple[List[str], str]]) -> List[str]:
    """Infer the output character inventory from training examples.

    Args:
        data: Encoded input/output examples.

    Returns:
        Sorted distinct characters occurring in output strings.
    """
    A: Set[str] = set()
    for _, out_str in data:
        A.update(out_str)          # characters used in outputs
    A.discard("")                  # just in case
    return sorted(A)


def learn_lcd_seal(
    data: List[Tuple[List[str], str]],
    max_len: int,
    alphabet: Optional[List[str]] = None,   # <-- changed
    identH: Dict[str, Set[str]] = {},
    verbose: bool = False,
    propagate_verbose: bool = False,
    solve_verbose: bool = False,
) -> Dict[str, Set[str]]:
    """Infer a length-constrained output assignment with LCD-SEAL.

    Args:
        data: Encoded input/output training examples.
        max_len: Maximum output-string length assigned to one symbol.
        alphabet: Permitted output characters; inferred from ``data`` if absent.
        identH: Baseline identity hypothesis updated with inferred assignments.
        verbose: Whether to print high-level learning diagnostics.
        propagate_verbose: Whether to print domain-propagation diagnostics.
        solve_verbose: Whether to print depth-first-search diagnostics.

    Returns:
        Updated hypothesis whose learned symbol domains are singletons. Returns
        ``None`` when no satisfying assignment exists.
    """

    if alphabet is None:                   # <-- added
        alphabet = infer_alphabet_from_data(data)

    EDGE = edge_symbols(data)

    # print("EDGE:", EDGE)
    # print("ALL syms:", sorted({s for inp,_ in data for s in inp}))

    if verbose:
        print("=" * 110)
        print("LEARN k-ISL deterministic subsequential function (EDGE fixed to epsilon)")
        print(f"max_len={max_len}, alphabet={alphabet}, #examples={len(data)}")
        print("EDGE =", sorted(EDGE, key=sym_sort_key))
        print("=" * 110)

    D0 = init_domains_context_aware_with_edges(
        data, max_len=max_len, alphabet=alphabet, EDGE=EDGE, verbose=verbose
    )
    if verbose:
        amb = sum(1 for s in D0 if s not in EDGE and len(D0[s]) > 1)
        tot = sum(len(vs) for vs in D0.values())
        mx  = max(len(vs) for vs in D0.values())
        print(f"[dbg] #syms={len(D0)}  #amb={amb}  total_candidates={tot}  max_domain={mx}")


    if verbose:
        print("\n[stage] PROPAGATE to convergence")
    Dprop = propagate_by_global_elimination(data, D0, max_len, EDGE, verbose=propagate_verbose)

    if verbose:
        print("\n[stage] SOLVE to singletons (DFS + propagation)")

    # Dprop["O3164"] = {"0+"} 
    sol = solve_to_singletons(data, Dprop, max_len, EDGE, verbose=solve_verbose)
    # NEW: preference-optimized repair pass (Option B)
    # sol = solve_len1_first_globally_optimal(data, Dprop, max_len, EDGE, verbose=verbose)




    if sol is None:
        return None

    out: Dict[str, Set[str]] = {}
    for sym in sorted(sol.keys(), key=sym_sort_key):
        if sym in EDGE:
            out[sym] = {""}
            continue
        vals = sol[sym]
        if len(vals) != 1:
            raise RuntimeError(f"Internal: non-singleton at end for {sym}: {vals}")
        out[sym] = set(vals)

    if verbose:
        print("\n" + "=" * 110)
        print("FINAL SOLUTION (your requested format; symbols present in data; EDGE forced to ''):")
        print(out)
        print("=" * 110)

    return compare_H(identH, out)


# Compatibility aliases for notebooks and scripts written before the
# dissertation terminology was applied to the public package. New code should
# import ``learn_prd_seal`` or ``learn_lcd_seal``.
learner_identity = learn_prd_seal
learn_kisl_dsf = learn_lcd_seal
