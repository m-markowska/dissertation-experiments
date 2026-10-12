"""Internal historical implementation shared by the public SEAL and FxF APIs."""

from __future__ import annotations
import heapq
from functools import lru_cache
from itertools import combinations
from pprint import pprint
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from . import data as prep
from . import preprocessing as pre_process
from .mappings import learn_lcd_seal, learn_prd_seal
from .fst import FST_feature



def encode_outputs(transformed: Sequence[List[Any]]) -> List[List[Any]]:
    """Replace each transition's output with a numbered placeholder.

    Args:
        transformed: Transition rows whose third item is the output label.

    Returns:
        Copies of the rows with outputs named ``O1``, ``O2``, and so on.
    """
    out = []
    for i, row in enumerate(transformed, start=1):
        new_row = row.copy()
        new_row[2] = f"O{i}"   # replace 3rd element
        out.append(new_row)
    return out


def edge_symbols(data: List[Tuple[List[str], str]]) -> Set[str]:
    """Collect symbols occurring at either edge of an encoded input.

    Args:
        data: Encoded input/output examples.

    Returns:
        First and last input symbols from all nonempty examples.
    """
    E: Set[str] = set()
    for inp, _ in data:
        if not inp:
            continue
        E.add(inp[0])
        E.add(inp[-1])
    return E


def validate_oi_out_pairs_no_interior_edge(
    data: List[Tuple[List[str], str]],
    *,
    return_details: bool = True,
    max_examples: int = 5,
) -> Tuple[bool, Dict[str, Any]]:
    """Check that boundary symbols never occur inside encoded inputs.

    Args:
        data: Encoded input/output examples to validate.
        return_details: Whether to include edge and offender information.
        max_examples: Maximum number of offending examples to report.

    Returns:
        A pair ``(ok, details)``. ``ok`` indicates whether the constraint
        holds. Details contain the edges, offender count, and a sample unless
        ``return_details`` is false.
    """
    EDGE = edge_symbols(data)

    offenders = []
    for ex_i, (inp, out) in enumerate(data, start=1):
        if len(inp) <= 2:
            continue
        for pos, sym in enumerate(inp[1:-1], start=1):
            if sym in EDGE:
                offenders.append({
                    "example_index": ex_i,
                    "symbol": sym,
                    "position": pos,
                    "input": inp,
                    "output": out,
                })
                break  # one offender per example is enough

    ok = (len(offenders) == 0)

    if not return_details:
        return ok, {}

    details: Dict[str, Any] = {
        "EDGE": sorted(EDGE),
        "num_offending_examples": len(offenders),
        "offenders_sample": offenders[:max_examples],
    }
    return ok, details


def _learn_seal_impl(
    feat: List,
    path_sigma: str,
    path_delta: str,
    all_feat_data: str,
    feat_k: int,
    *,
    direction: Any="L2R",
    check_training: Any=True,
    mode: str = "lcd-seal",
    learner: Any = None,
) -> Tuple[Any, Any]:
    """Learn one feature-level transducer with SEAL.

    This is one complete SEAL invocation for a fixed target feature, input
    projection, locality width, and processing direction. The first item in
    ``feat`` is the target output feature phi; the full list is the input
    feature set Phi.

    Args:
        feat: Ordered feature names used to project segment representations.
        path_sigma: Path to the input segment inventory.
        path_delta: Path to the output segment inventory.
        all_feat_data: Path to feature-encoded training pairs.
        feat_k: Locality width used to construct the encoded transducer.
        direction: Direction label recorded in diagnostic results.
        check_training: Whether to evaluate the result on its training pairs.
        mode: Output-distribution mode, ``"prd-seal"`` or ``"lcd-seal"``.
        learner: Deprecated compatibility spelling for ``mode``. Historical
            values ``"identity"`` and ``"dsf"`` select PRD-SEAL and LCD-SEAL,
            respectively.

    Returns:
        A ``(status, information)`` pair. Information includes the feature
        configuration, inferred output map, transitions, transducer, and
        evaluation message, or failure diagnostics when learning cannot finish.
    """
    
    # print(f"[{direction}] FEAT: ", feat)
    # print(f"[{direction}] IDENTITY FEATURE =", feat[0])
    # print(f"[{direction}] k: ", feat_k)
    # if feat_k == 3:
    #     print('***'*100)
    #     print('ENTERING K=3')
    #     print('***'*100)
    org_data = prep.read_org_data(all_feat_data)
    features = pre_process.features(path_sigma)
  
    feat_pairs = prep.extract_feat_pairs(feat, prep.feature_id(path_delta), org_data)
    # pprint(feat_pairs)
    # for pair in feat_pairs:
    #     if pair[0] == [('<',), ('+00--',), ('--+00',), ('+00-0',), ('---00',), ('-+-00',), ('--+00',), ('>',)]:
    #         print(pair)
    seen_io = {}
    for inp, out in feat_pairs:
        key = tuple(inp)  # inp is a list of tuples; tuple(...) is hashable
        if key in seen_io and seen_io[key] != out:
            # print("inp-out:")
            # print(inp)
            # print(out)
            # print("NOT FUNCTIONAL feat_pairs for feat =", feat)
            return (
        "failed",
        {
            "direction": direction,
            "feat": feat,
            "k": feat_k,
            "error_type": "NOT_FUNCTIONAL_FEAT_PAIRS",
            "error_msg": f"conflict for input {inp}: {seen_io[key]} vs {out}",
            "learned_transitions": None,
            "predicted_O_map": None,
        },
    )
        seen_io[key] = out
    # print('seen_io: ', seen_io)
    # return

    sigma_feat = prep.transform_alphabet(prep.get_alphabet(path_sigma, 'feature', feat))
    delta_feat = prep.transform_alphabet(prep.get_alphabet(path_delta, 'feature', feat))

    # print('sigma_feat: ',sigma_feat)
    # feat_k = 3
    states_feat = pre_process.states_gen(sigma_feat, feat_k) 
    # print('states_feat ', len(states_feat), states_feat)
    # return
    trans_k_feat = pre_process.gen_k_trans_ident(sigma_feat, feat_k)
    # print('trans_k:')
    # pprint(trans_k_feat)
    encoded_trans = encode_outputs(trans_k_feat)
    # pprint(encoded_trans)
    # states = pre_process.states_gen()
    # pprint(type(encoded_trans))
    # return
    # + [('<<',)] --> cuz i removed it in build k-trans
    FST_encoded = FST_feature(states_feat + [('<<',)], sigma_feat, delta_feat, '<<', '>', encoded_trans, feat)
        
    # pprint(feat_pairs)
    # return
    Oi_out_pairs = FST_encoded.gen_encoded_pairs(feat_pairs)
    # return
    # for i in range(len(Oi_out_pairs)):
    #     print(Oi_out_pairs[i])
    #     print(feat_pairs[i])
    # pprint(Oi_out_pairs)
    # return
    # return
    # print('FEAT_PAIRS')
    # pprint(feat_pairs)
    # return
    ok, info = validate_oi_out_pairs_no_interior_edge(Oi_out_pairs)
    if not ok:
        print("Skipping combo: interior EDGE symbol found.")
        print("EDGE =", info["EDGE"])
        print("Sample offenders:", info["offenders_sample"])
        return (False, ["BAD_OI_OUT_PAIRS_INTERIOR_EDGE", info])
    # print('Oi-out-pairs: ')
    # pprint(Oi_out_pairs)


    # if output == True:
    #     return 'WE FUCKING GOT IT'
    Hident = prep.map_Oi_to_outputs(encoded_trans, trans_k_feat)
    # print('Hident: ')
    # pprint(Hident)
    # predicted = dict(learn_prd_seal(Oi_out_pairs, Hident).items())
    # pprint(predicted)
    # print(len(Hident) == len(predicted))
    # pprint(encoded_trans)
    # extr_tr = pre_process.extract_feats_trans_one_output(trans_onward, feat, sigma_inventory, 3)
    # FST_learned = FST_feature(states_feat + [('<<',)], sigma_feat, delta_feat, '<<', '>', extr_tr, feat)


    selected_mode = learner if learner is not None else mode
    normalized_mode = {
        "identity": "prd-seal",
        "dsf": "lcd-seal",
        "prd": "prd-seal",
        "lcd": "lcd-seal",
    }.get(selected_mode, selected_mode)
    if normalized_mode not in {"prd-seal", "lcd-seal"}:
        raise ValueError(
            f"Unknown SEAL mode {selected_mode!r}; expected 'prd-seal' or 'lcd-seal'."
        )

    try:
        # print('Trying to learn with second learner tyep')
        if normalized_mode == "prd-seal":
            predicted = dict(learn_prd_seal(Oi_out_pairs, Hident).items())
        else:
            predicted = learn_lcd_seal(Oi_out_pairs, feat_k, identH=Hident)
        # pprint(predicted)

    except ValueError as e:
        return (
            "failed",
            {
                "direction": direction,
                "feat": feat,
                "k": feat_k,
                "error_type": "Impossible assignment",
                "error_msg": str(e),
                "learned_transitions": None,
                "predicted_O_map": None,
            },
        )

    if predicted is None:
        return (
            "failed",
            {
                "direction": direction,
                "feat": feat,
                "k": feat_k,
                "error_type": "Empty assignemnt",
                "error_msg": "LCD-SEAL returned None (no solution found)",
                "learned_transitions": None,
                "predicted_O_map": None,
            },
        )

    # if feat_k > 1:
    #     predicted[get_empty_string_O(encoded_trans)] = {''}

    # extr_tr = pre_process.extract_feats_trans_one_output(trans_onward, feat, sigma_inventory, 3)
    # FST_learned = FST_feature(states_feat + [('<<',)], sigma_feat, delta_feat, '<<', '>', extr_tr, feat)

    FST_learned = FST_feature(states_feat + [('<<',)], sigma_feat, delta_feat, '<<', '>', dict_to_trans(encoded_trans, predicted), feat)
    # pprint(FST_learned.transitions)
    # print('states:')
    # print(learned_kDFT.states)
    # print('sigma:')
    # print(learned_kDFT.sigma)
    # print('delta')
    # print(learned_kDFT.delta)
    # print('trans: ')
    # for trans in FST_learned.transitions:
    #     print(trans)
    # pprint(make_onward_global_single_feature(FST_learned.transitions, 'cor'))
    # for i in make_onward_global_single_feature(FST_learned.transitions, 'cor'):
    #     if i[0] == ('<',) and i[1] == ('0+++0',):
    #         print('1', i)
    #     elif i[0] == ('0+++0',) and i[1] == ('0+0+0',):
    #         print('2', i)
    #     elif i[0] == ('0+++0', '0+0+0') and i[1] == ('--0--',):
    #         print('3', i)
    #     elif i[0] == ('0+0+0', '--0--') and i[1] == ('0+++0',):
    #         print('4', i)
    #     elif i[0] == ('--0--','0+++0') and i[1] == ('++0+-',):
    #         print('5', i)
    #     elif i[0] == ('0+++0', '++0+-') and i[1] == ('0+++0',):
    #         print('6', i)
    #     elif i[0] == ('++0+-', '0+++0') and i[1] == ('>',):
    #         print('7', i)

    # return
    # print('pairs:')
    # print(len(feat_pairs))
    # for pair in feat_pairs:
    #     print(pair)
    # return
    # print("processing input: [('<',), ('0-0',), ('-+0',), ('-+0',), ('-+0',), ('0++',), ('-+0',), ('>',)]")
    # print(learned_kDFT.transform_and_process_input([('<',), ('0-0',), ('-+0',), ('-+0',), ('-+0',), ('0++',), ('-+0',), ('>',)]))
    # print('FINAL OUTPUT insdie one_feat_learn: ', output)
    # return dict_to_trans(encoded_trans, predicted)
    # print(evaluate_transducer(FST_learned, feat_pairs))
    # return evaluate_transducer(FST_learned, feat_pairs)
    # print('calculating....')
    # for i in FST_learned.transitions:
    #     print(i)
    # return
    if check_training:
        eval_result = evaluate_transducer(FST_learned, feat_pairs)  # ("passed"/"failed", msg)
    else:
        eval_result = ("passed", "TRAINING_EVAL_SKIPPED")
    # print('eval_result: ', eval_result)
    # return 
    # pprint(make_onward_global_single_feature(extr_tr))
    # print('FEAT_PAIRS')
    # for i in feat_pairs:
    #     print(i)
    # # print('Oi-out-pairs: ')
    # pprint(Oi_out_pairs)
    # for t in FST_learned.transitions:
    #     print(t)

    return (
        eval_result[0],
        {
            "direction": direction,
            "feat": feat,
            "k": feat_k,
            "predicted_O_map": predicted,                 # keep for debugging if you want
            "encoded_trans": encoded_trans,               # optional
            "learned_transitions": FST_learned.transitions,
            "fst": FST_learned,                           # object itself (for later use)
            "eval_msg": eval_result[1],
        }
    )


def dict_to_trans(encoded_trans: Sequence[Any], learned_output: Any) -> List[Any]:
    """Insert learned output values into encoded transition rows.

    Args:
        encoded_trans: Transitions whose third item is an output placeholder.
        learned_output: Mapping from placeholders to learned output sets.

    Returns:
        Transition rows with placeholders replaced by learned values.
    """
    learned_trans = []
    for trans in encoded_trans:
        # print('trans: ', trans)
        output = trans[2]
        if output in learned_output.keys():
            # print('We learned it: ', output, '-->', learned_output[output])
            new_trans =  [trans[0], trans[1], list(learned_output[output]), trans[3]]
            # print('new trans: ')
            # print(new_trans)
        learned_trans.append(new_trans)
    return learned_trans


def generate_combinations(features_all: Sequence[str], picked: Sequence[str], l: int) -> List[List[str]]:
    """Extend selected features to every combination of a target length.

    Args:
        features_all: Complete ordered feature inventory.
        picked: Features required in every returned combination.
        l: Required total number of features in each combination.

    Returns:
        Feature lists beginning with ``picked``, or an empty list when
        ``picked`` is longer than ``l``.
    """
    remaining = [f for f in features_all if f not in picked]
    needed = l - len(picked)
    if needed < 0:
        return []
    return [picked + list(combo) for combo in combinations(remaining, needed)]


@lru_cache(maxsize=None)
def estimate_num_states(feat_combo_tuple: tuple[str, ...], feat_k: int, sigma_inventory: str) -> int:
    """Estimate the state count for a feature projection and locality width.

    Args:
        feat_combo_tuple: Feature names defining the projection.
        feat_k: Locality width used to generate states.
        sigma_inventory: Path to the input segment inventory.

    Returns:
        Number of generated states for the projected input alphabet.
    """
    feat_combo = list(feat_combo_tuple)
    sigma_feat = prep.transform_alphabet(prep.get_alphabet(sigma_inventory, "feature", feat_combo))
    states_feat = pre_process.states_gen(sigma_feat, feat_k)
    # print('sigma_feat: ', sigma_feat)
    # print('states_feat: ', states_feat)
    return len(states_feat)  # + [('<<',)] ; remove +1 if you don't count it


def iter_candidates_by_num_states(
    base_feat: list[str],
    features_all: list[str],
    *,
    sigma_inventory: str,
    k_min: int = 1,
    k_max: int = 4,
    l_max: int = 5,
) -> Iterable[Any]:
    """Yield candidates in increasing state-count order.

    Args:
        base_feat: Features required in every candidate.
        features_all: Complete feature inventory available for expansion.
        sigma_inventory: Path to the input segment inventory.
        k_min: Smallest locality width to consider.
        k_max: Largest locality width to consider.
        l_max: Largest feature-set size to consider.

    Returns:
        An iterator of ``(feature_list, k, state_count)`` triples in
        deterministic order.
    """
    candidates = []
    l_min = len(base_feat)

    for k in range(k_min, k_max + 1):
        for l in range(l_min, l_max + 1):
            for combo in generate_combinations(features_all, base_feat, l):
                n_states = estimate_num_states(tuple(combo), k, sigma_inventory)
                # tie-breakers keep order deterministic
                candidates.append((n_states, len(combo), k, combo))

    candidates.sort()
    for n_states, _flen, k, combo in candidates:
        yield combo, k, n_states


def _learn_fxf_impl(
    sigma_inventory: str,
    delta_inventory: str,
    all_feat_data: str,
    *,
    all_feat_data_reversed: str | None = None,   # <-- NEW for R2L
    require_both: bool = True,                   # <-- NEW (policy)
    base_features: list[str] | None = None,
    verbose_search: bool = False,
    k_min: int = 1,
    k_max: int = 4,
    l_max: int = 5,
    check_training: bool = True,
    print_learned_transitions: bool = True,
    mode: str = "lcd-seal",
    feature_learner: Any = _learn_seal_impl,
    learner: Any = None,
    preferred_direction: str = "R2L",
) -> Any:
    """Apply the learner-agnostic Factor by Feature architecture.

    FxF decomposes a transduction into one feature-level learning problem for
    each target feature. ``feature_learner`` supplies the underlying learner;
    SEAL is the default implementation used by the dissertation experiments.

    Args:
        sigma_inventory: Path to the input segment inventory.
        delta_inventory: Path to the output segment inventory.
        all_feat_data: Path to left-to-right encoded training pairs.
        all_feat_data_reversed: Optional right-to-left encoded training pairs.
        require_both: Whether both available directions must succeed.
        base_features: Features to learn; defaults to inventory features.
        verbose_search: Whether to print candidate-expansion diagnostics.
        k_min: Initial locality width.
        k_max: Maximum locality width considered.
        l_max: Maximum number of features in a specification.
        check_training: Whether each candidate is tested on training data.
        print_learned_transitions: Whether successful transitions are printed.
        mode: Mode forwarded to the feature learner. SEAL accepts
            ``"prd-seal"`` and ``"lcd-seal"``.
        feature_learner: Callable used to infer each feature-level transducer.
            It must implement the documented FxF feature-learner protocol.
        learner: Deprecated compatibility spelling for ``mode``.
        preferred_direction: Direction evaluated first, ``"L2R"`` or ``"R2L"``.

    Returns:
        Mapping from each base feature to its first successful candidate,
        directional outcomes, and the candidates tested in search order.
    """
    import heapq

    selected_mode = learner if learner is not None else mode
    final_result = {}
    print(f"FEATURE LEARNER: {getattr(feature_learner, '__name__', type(feature_learner).__name__)}")
    print(f"MODE: {selected_mode}")

    if base_features is None:
        base_features = pre_process.features(sigma_inventory)

    features_all = pre_process.features(sigma_inventory)


    # def eval_candidate(combo: list[str], k: int):
    #     print('combo: ', combo)
    #     outcomes = {}

    #     def pack(info):
    #         if isinstance(info, dict):
    #             return {"learned_transitions": info.get("learned_transitions")}
    #         return {"learned_transitions": None, "info": info}

    #     status_l2r, info_l2r = learn_seal(combo, sigma_inventory, delta_inventory, all_feat_data, k, direction="L2R")
    #     outcomes["L2R"] = (status_l2r, pack(info_l2r))

    #     if all_feat_data_reversed is not None:
    #         status_r2l, info_r2l = learn_seal(combo, sigma_inventory, delta_inventory, all_feat_data_reversed, k, direction="R2L")
    #         outcomes["R2L"] = (status_r2l, pack(info_r2l))
    #     else:
    #         status_r2l = "passed"

    #     passed_l2r = (status_l2r == "passed")
    #     passed_r2l = (status_r2l == "passed")

    #     passed_any  = passed_l2r or passed_r2l
    #     passed_both = passed_l2r and passed_r2l

    #     status = "passed" if passed_any else "failed"
    #     return status, outcomes, passed_both
    def eval_candidate(combo: list[str], k: int) -> Any:
        """Evaluate one feature combination in the configured directions.

        Args:
            combo: Ordered feature specification to evaluate.
            k: Locality width for this candidate.

        Returns:
            Overall status, per-direction outcomes, and whether both passed.
        """
        outcomes = {}

        def pack(info: Any) -> Dict[str, Any]:
            """Reduce learner information to transition diagnostics.

            Args:
                info: Detailed result returned by :func:`learn_seal`.

            Returns:
                Learned transitions, plus the original diagnostic value when
                the result is not a dictionary.
            """
            if isinstance(info, dict):
                return {"learned_transitions": info.get("learned_transitions")}
            return {"learned_transitions": None, "info": info}

        if preferred_direction == "L2R":
            status_l2r, info_l2r = feature_learner(
                combo,
                sigma_inventory,
                delta_inventory,
                all_feat_data,
                k,
                direction="L2R",
                check_training=check_training,
                mode=selected_mode,
            )
            outcomes["L2R"] = (status_l2r, pack(info_l2r))

            if not require_both and status_l2r == "passed":
                return "passed", outcomes, False

            if all_feat_data_reversed is not None:
                status_r2l, info_r2l = feature_learner(
                    combo,
                    sigma_inventory,
                    delta_inventory,
                    all_feat_data_reversed,
                    k,
                    direction="R2L",
                    check_training=check_training,
                    mode=selected_mode,
                )
                outcomes["R2L"] = (status_r2l, pack(info_r2l))
            else:
                status_r2l = "passed"
                outcomes["R2L"] = ("passed", {"learned_transitions": None})

            passed_l2r = (status_l2r == "passed")
            passed_r2l = (status_r2l == "passed")
            passed_any = passed_l2r or passed_r2l
            passed_both = passed_l2r and passed_r2l

            if require_both:
                status = "passed" if passed_both else "failed"
            else:
                status = "passed" if passed_any else "failed"
            return status, outcomes, passed_both

        if all_feat_data_reversed is not None:
            status_r2l, info_r2l = feature_learner(
                combo,
                sigma_inventory,
                delta_inventory,
                all_feat_data_reversed,
                k,
                direction="R2L",
                check_training=check_training,
                mode=selected_mode,
            )
            outcomes["R2L"] = (status_r2l, pack(info_r2l))

            if not require_both and status_r2l == "passed":
                return "passed", outcomes, False
        else:
            status_r2l = "passed"
            outcomes["R2L"] = ("passed", {"learned_transitions": None})

        status_l2r, info_l2r = feature_learner(
            combo,
            sigma_inventory,
            delta_inventory,
            all_feat_data,
            k,
            direction="L2R",
            check_training=check_training,
            mode=selected_mode,
        )
        outcomes["L2R"] = (status_l2r, pack(info_l2r))

        passed_l2r = (status_l2r == "passed")
        passed_r2l = (status_r2l == "passed")

        passed_any  = passed_l2r or passed_r2l
        passed_both = passed_l2r and passed_r2l

        if require_both:
            status = "passed" if passed_both else "failed"
        else:
            status = "passed" if passed_any else "failed"
        return status, outcomes, passed_both





    def normalize_combo(base_feat: list[str], combo: list[str]) -> list[str]:
        """Place the base feature first and sort unique remaining features.

        Args:
            base_feat: Nonempty list whose first item is required.
            combo: Candidate feature list to normalize.

        Returns:
            Deterministic feature list beginning with ``base_feat[0]``.
        """
        base = base_feat[0]
        rest = [f for f in combo if f != base]
        rest = sorted(set(rest))
        return [base] + rest


    # best_one = None
    # best_one_states = None
    winner = None
    for base in base_features:
        base_feat = [base]
        min_combo_len = len(base_feat)
        print("\n" + "=" * 100)
        print(f"BASE FEAT: {base_feat}")
        print("=" * 100)
        if base_feat == ['high']:
            base_feat = ['high', 'nasal', 'round', 'tap', 'voice']
            k_min = 3
            min_combo_len = len(base_feat)
        elif base_feat == ['tense']:
            base_feat = ['tense', 'nasal', 'round', 'tap', 'voice']
            k_min = 3
            min_combo_len = len(base_feat)
        elif base_feat == ['voice']:
            base_feat = ['voice', 'son']
            k_min = 2
            min_combo_len = len(base_feat)
        else:
            k_min = 1
            min_combo_len = len(base_feat)




        # if base_feat == ['ant']:
        #     base_feat = ['ant', 'dor', 'front', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['back']:
        #     base_feat = ['back', 'dor', 'front', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['cont']:
        #     base_feat = ['cont', 'nasal', 'son', 'voice', 'dor']
        #     k_min = 2
        # elif base_feat == ['cor']:
        #     base_feat = ['cor', 'son', 'front', 'voice', 'cont']
        #     k_min = 3
        # elif base_feat == ['delrel']:
        #     base_feat = ['delrel', 'nasal', 'son', 'voice', 'dor']
        #     k_min = 2
        # elif base_feat == ['distr']:
        #     base_feat = ['distr', 'dor', 'front', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['dor']:
        #     base_feat = ['dor', 'ant', 'front', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['front']:
        #     base_feat = ['front', 'ant', 'dor', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['high']:
        #     base_feat = ['high', 'lab', 'front', 'voice', 'son']
        #     k_min = 2
        # elif base_feat == ['lab']:
        #     base_feat = ['lab', 'high', 'front', 'voice', 'son']
        #     k_min = 2
        # elif base_feat == ['low']:
        #     base_feat = ['low', 'cont', 'front', 'voice', 'son']
        #     k_min = 2
        # elif base_feat == ['strid']:
        #     base_feat = ['strid', 'cor', 'front', 'voice', 'nasal']
        #     k_min = 3
        # elif base_feat == ['voice']:
        #     base_feat = ['voice', 'nasal', 'cont']
        #     k_min = 2
        # else:
        #     k_min = 1




        # if base_feat == ['ant']:
        #     base_feat = ['ant', 'dor', 'front', 'son']
        #     k_min = 3
        # elif base_feat == ['back']:
        #     base_feat = ['back', 'dor', 'front', 'son']
        #     k_min = 3
        # elif base_feat == ['cont']:
        #     base_feat = ['cont', 'son', 'voice']
        #     k_min = 2
        # elif base_feat == ['cor']:
        #     base_feat = ['cor', 'son', 'front', 'voice', 'lab']
        #     k_min = 3
        # elif base_feat == ['delrel']:
        #     base_feat = ['delrel', 'cont', 'voice']
        #     k_min = 2
        # elif base_feat == ['distr']:
        #     base_feat = ['distr', 'dor', 'front', 'son']
        #     k_min = 3
        # elif base_feat == ['dor']:
        #     base_feat = ['dor', 'son', 'front', 'voice', 'lab']
        #     k_min = 3
        # elif base_feat == ['front']:
        #     base_feat = ['front', 'dor', 'voice', 'son']
        #     k_min = 3
        # elif base_feat == ['high']:
        #     base_feat = ['high', 'son', 'lab']
        #     k_min = 2
        # elif base_feat == ['lab']:
        #     base_feat = ['lab', 'son', 'labdent']
        #     k_min = 2
        # elif base_feat == ['low']:
        #     base_feat = ['low', 'son', 'lab']
        #     k_min = 2
        # elif base_feat == ['strid']:
        #     base_feat = ['strid', 'dor', 'front', 'son']
        #     k_min = 3
        # elif base_feat == ['voice']:
        #     base_feat = ['voice', 'son', 'nasal', 'labdent']
        #     k_min = 2
        # elif base_feat == ['approx']:
        #     k_min = 1
        # elif base_feat == ['cons']:
        #     k_min = 1
        # elif base_feat == ['constrgl']:
        #     k_min = 1
        # elif base_feat == ['labdent']:
        #     k_min = 1
        # elif base_feat == ['lat']:
        #     k_min = 1
        # elif base_feat == ['nasal']:
        #     k_min = 1
        # elif base_feat == ['round']:
        #     k_min = 1
        # elif base_feat == ['son']:
        #     k_min = 1
        # elif base_feat == ['spreadgl']:
        #     k_min = 1
        # elif base_feat == ['tap']:
        #     k_min = 1
        # elif base_feat == ['tense']:
        #     k_min = 1
        # elif base_feat == ['trill']:
        #     k_min = 1

        # if base_feat == ['lat']:
        #     k_min = 3
        # else:
        #     base_feat = [base_feat[0], 'lat']
        #     k_min = 3

        tested_in_order = []

        if min_combo_len > len(base_feat):
            high_tense_winner = None
            print("\n" + "-" * 90)
            print(
                f"STAGE 1 / SEARCH COMBOS: min_len={min_combo_len} "
                f"k_min={k_min}  base={base_feat}"
            )
            print("-" * 90)

            for combo, k, n_states in iter_candidates_by_num_states(
                base_feat,
                features_all,
                sigma_inventory=sigma_inventory,
                k_min=k_min,
                k_max=k_max,
                l_max=l_max,
            ):
                if len(combo) < min_combo_len:
                    continue

                if verbose_search:
                    print(
                        "\n" + "=" * 90
                        + f"\nTRY: states={n_states}  k={k}  feat={combo}"
                        + "\n" + "=" * 90
                    )

                status, outcomes, passed_both = eval_candidate(combo, k)
                passed_any = (status == "passed")

                tested_in_order.append({
                    "feat": combo,
                    "feat_k": k,
                    "states": n_states,
                    "outcome": {
                        "status": status,
                        "passed_any": passed_any,
                        "passed_both": passed_both,
                        "outcomes": outcomes,
                    },
                })

                if status == "passed":
                    high_tense_winner = tested_in_order[-1]
                    print("\n✅ FOUND WINNER (stopping search).")
                    print(f"WINNER feat={combo}  k={k}  states={n_states}")
                    break

            final_result[tuple(base_feat)] = {
                "result": "passed" if high_tense_winner is not None else False,
                "winner": high_tense_winner,
                "tested_in_order": tested_in_order,
            }
            continue

        # ----------------------------
        # STAGE 1: try base_feat, k=k_min
        # ----------------------------
        base_norm = normalize_combo(base_feat, base_feat)
        n_states_first = estimate_num_states(tuple(base_norm), k_min, sigma_inventory)

        print("\n" + "-" * 90)
        print(f"STAGE 1 / TRY FIRST: states={n_states_first}  k={k_min}  feat={base_norm}")
        print("-" * 90)

        status_first, outcomes_first, passed_both_first = eval_candidate(base_norm, k_min)
        passed_any_first = (status_first == "passed")

        # print(f"RESULT FIRST: ('{'passed' if passed_any_first else 'failed'}', {outcomes_first})")

        tested_in_order.append({
            "feat": base_norm,
            "feat_k": k_min,
            "states": n_states_first,
            "outcome": {
                "outcomes": outcomes_first,
                "passed_any": passed_any_first,
                "passed_both": passed_both_first,
            },
        })

        if passed_any_first:
            if check_training:
                print("\n✅ FOUND WINNER (stopping search).")
                print(f"WINNER feat={base_norm}  k={k_min}  states={n_states_first}")
            else:
                print("\nFOUND CANDIDATE (training check skipped; testing heldout next).")
                print(f"CANDIDATE feat={base_norm}  k={k_min}  states={n_states_first}")


            if print_learned_transitions:
                # Print transitions for BOTH directions (even if one failed)
                for direction in ("L2R", "R2L"):
                    if direction not in outcomes_first:
                        continue
                    st, info = outcomes_first[direction]

                    print(f"[{direction}] FEAT:  {base_norm}")
                    print(f"[{direction}] IDENTITY FEATURE = {base_norm[0]}")
                    print(f"[{direction}] k:  {k_min}\n")

                    learned = info.get("learned_transitions") if isinstance(info, dict) else None
                    if learned is None:
                        print(f"--- {direction} learned transitions (n=0) ---")
                        print("None\n")
                    else:
                        print(f"--- {direction} learned transitions (n={len(learned)}) ---")
                        pprint(learned)
                        print()

            final_result[tuple(base_feat)] = {
                "result": "passed",
                "winner": tested_in_order[-1],
                "tested_in_order": tested_in_order,
            }
            continue


        # ---------------------------------------------------------
        # STAGE 2: Best-first search by #states using a min-heap
        # ---------------------------------------------------------
        print("\n" + "-" * 90)
        print("STAGE 2 / HEAP SEARCH: smallest #states first")
        print("-" * 90)

        heap = []
        seen = set()
        push_id = 0  # deterministic tie-break

        def push_candidate(base_feat: list[str], combo: list[str], k: int, reason: str) -> None:
            """Add an unseen normalized candidate to the search heap.

            Args:
                base_feat: Required base feature specification.
                combo: Candidate feature specification.
                k: Candidate locality width.
                reason: Diagnostic description of how the candidate arose.

            Returns:
                None.
            """
            nonlocal push_id

            norm = normalize_combo(base_feat, combo)
            key = (tuple(norm), k)
            if key in seen:
                return
            seen.add(key)

            n_states = estimate_num_states(tuple(norm), k, sigma_inventory)
            heapq.heappush(heap, (n_states, len(norm), k, push_id, norm))
            push_id += 1
            if verbose_search:
                print(f"  PUSH  states={n_states:<4} k={k} feat={norm}   <-- {reason}")

        def expand_neighbors(base_feat: list[str], combo: list[str], k: int) -> None:
            """Push valid one-step neighbors of a failed candidate.

            Args:
                base_feat: Required base feature specification.
                combo: Failed feature specification to expand.
                k: Locality width of the failed candidate.

            Returns:
                None.
            """
            combo = normalize_combo(base_feat, combo)
            if verbose_search:
                print(
                    f"\nEXPAND from failed: states={estimate_num_states(tuple(combo), k, sigma_inventory)} "
                    f"k={k} feat={combo}"
                )

            # Neighbor 1: increase k
            if k < k_max:
                push_candidate(base_feat, combo, k + 1, reason="neighbor: increase k")

            # Neighbor 2: add one new feature (respect l_max)
            if len(combo) < l_max:
                for f in features_all:
                    if f not in combo:
                        push_candidate(base_feat, combo + [f], k, reason=f"neighbor: add feature {f!r}")

        # =========================================================
        # IMPORTANT CHANGE:
        # If k=1 fails, jump straight to k=2 (NO k=1 expansions)
        # =========================================================
        if k_min == 1:
            if k_min < k_max:
                push_candidate(base_feat, base_norm, k_min + 1, reason="k=1 failed → jump to k=2 (start heap)")
            else:
                # nowhere to go
                final_result[tuple(base_feat)] = {
                    "result": False,
                    "winner": None,
                    "tested_in_order": tested_in_order,
                }
                continue
        else:
            # If k_min is not 1, just start expanding from the failed first attempt as usual.
            expand_neighbors(base_feat, base_norm, k_min)

        # winner = None

        # best_one = None          # store the tested_in_order entry for a one-direction pass
        # best_one_states = None   # the n_states where we first saw a one-direction pass

        while heap:
            n_states, _flen, k, _pid, combo = heapq.heappop(heap)
            # If we already found a one-direction pass at some smaller/equal #states,
            # and now we're moving to larger #states, return that fallback.
            # if best_one is not None and n_states > best_one_states:
            #     winner = best_one
            #     print("\n✅ Taking ONE-direction fallback (no BOTH found at same #states).")
            #     print(f"WINNER feat={winner['feat']}  k={winner['feat_k']}  states={best_one_states}")
            #     break

            if verbose_search:
                print("\n" + "=" * 90)
                print(f"POP / TRY: states={n_states}  k={k}  feat={combo}")
                print(f"HEAP size after pop: {len(heap)}")
                print("=" * 90)

            # out = learn_seal(combo, sigma_inventory, delta_inventory, all_feat_data, k)
            # status, outcomes = eval_candidate(combo, k)
            # out = (status, outcomes)
            # status, outcomes, passed_both = eval_candidate(combo, k)
            # out = (status, outcomes, passed_both)

            # tested_in_order.append({
            #     "feat": combo,
            #     "feat_k": k,
            #     "states": n_states,
            #     "outcome": out,
            # })
            status, outcomes, passed_both = eval_candidate(combo, k)
            passed_any = (status == "passed")

            tested_in_order.append({
                "feat": combo,
                "feat_k": k,
                "states": n_states,
                "outcome": {
                    "status": status,          # "passed" iff at least one direction passed
                    "passed_both": passed_both,
                    "outcomes": outcomes,      # contains L2R/R2L statuses + learned transitions
                },
            })

            # Stop as soon as at least ONE direction works
            if status == "passed":
                winner = tested_in_order[-1]

                if check_training:
                    print("\n✅ FOUND WINNER (stopping search).")
                else:
                    print("\nFOUND CANDIDATE (training check skipped; testing heldout next).")
                # if passed_both:
                #     print("Directions: L2R ✅  R2L ✅")
                # else:
                #     # figure out which one passed/failed for the message
                #     l2r_ok = outcomes.get("L2R", ("failed", {}))[0] == "passed"
                #     r2l_ok = outcomes.get("R2L", ("failed", {}))[0] == "passed"
                #     print(f"Directions: L2R {'✅' if l2r_ok else '❌'}  R2L {'✅' if r2l_ok else '❌'}")

                # print(f"WINNER feat={combo}  k={k}  states={n_states}")
                if check_training:
                    print(f"WINNER feat={combo}  k={k}")
                else:
                    print(f"CANDIDATE feat={combo}  k={k}")

                if print_learned_transitions:
                    # (optional) print transitions like before
                    for direction, (st, info) in outcomes.items():
                        print(f"[{direction}] FEAT:  {combo}")
                        print(f"[{direction}] IDENTITY FEATURE = {combo[0]}")
                        print(f"[{direction}] k:  {k}\n")

                        learned = info.get("learned_transitions") if isinstance(info, dict) else None
                        if learned is None:
                            print(f"--- {direction} learned transitions (n=0) ---")
                            print("None\n")
                        else:
                            print(f"--- {direction} learned transitions (n={len(learned)}) ---")
                            pprint(learned)
                            print()

                break

            # Only expand neighbors if NEITHER direction worked
            expand_neighbors(base_feat, combo, k)
                        # print(f"RESULT: {out}") ----> # uncommnet if more info needed


            # if out[0] == "passed":
            #     print("\n✅ FOUND WINNER (stopping search).")
            #     print(f"WINNER feat={combo}  k={k}")

            #     for direction, (st, info) in out[1].items():
            #         if st == "passed":
            #             print(f"[{direction}] FEAT: ", combo)
            #             print(f"[{direction}] IDENTITY FEATURE =", combo[0])
            #             print(f"[{direction}] k: ", k)

            #             print(f"\n--- {direction} learned transitions (n={len(info['learned_transitions'])}) ---")
            #             pprint(info["learned_transitions"])

            #     break

            # if out[0] == "passed":
            #     if out[2]:  # passed_both
            #         winner = tested_in_order[-1]
            #         print("\n✅ FOUND WINNER (BOTH directions).")
            #         print(f"WINNER feat={combo}  k={k}  states={n_states}")
            #         break

            #     # passed in exactly one direction → store fallback, but keep searching
            #     if best_one is None:
            #         best_one = tested_in_order[-1]
            #         best_one_states = n_states
            #         print("\n⭐ Found ONE-direction pass (keeping as fallback).")
            #         print(f"FALLBACK feat={combo}  k={k}  states={n_states}")

            # expand_neighbors(base_feat, combo, k)
            if verbose_search:
                print(f"\nHEAP size after expand: {len(heap)}")
                print(f"Seen candidates so far: {len(seen)}")

        # if winner is None and best_one is not None:
        #     winner = best_one

        final_result[tuple(base_feat)] = {
            # "result": "passed" if winner else False,
            "result": "passed" if winner is not None else False,
            "winner": winner,
            "tested_in_order": tested_in_order,
        }

    return final_result


def normalize_combo(base_feat: list[str], combo: list[str]) -> list[str]:
    """Place the base feature first and remove later duplicates.

    Args:
        base_feat: Nonempty list whose first item is required.
        combo: Candidate feature list to normalize.

    Returns:
        Feature list beginning with ``base_feat[0]`` and retaining the original
        relative order of the other first-occurring features.
    """
    base = base_feat[0]
    rest = [f for f in combo if f != base]
    # preserve order of rest as given
    seen_local = set()
    rest2 = []
    for f in rest:
        if f not in seen_local:
            rest2.append(f)
            seen_local.add(f)
    return [base] + rest2


def evaluate_transducer(FST_feat: FST_feature, feat_pairs: Any) -> Tuple[str, Optional[str]]:
    """Evaluate a feature transducer on encoded examples.

    Args:
        FST_feat: Feature transducer to execute.
        feat_pairs: Iterable of encoded input and expected-output pairs.

    Returns:
        ``("passed", None)`` when every output matches; otherwise a failed
        status and a message describing the first mismatch.
    """
    for left_str, right_str in feat_pairs:
        # print('input: ', left_str)
        # print('output: ', right_str)
        got = FST_feat.process_input_feature_prod(left_str)[0]
        # print('learned: ', got)
        if got != right_str:
            # don't crash the whole search; just report failure
            return ("failed", f"Failed on {left_str} -> {right_str}, got {got}")
    return ("passed", None)


# Compatibility aliases for code written before the public API adopted the
# terminology used in the dissertation. They are intentionally omitted from
# ``seal.__all__``.
learn_one_feat = _learn_seal_impl
flex_learn = _learn_fxf_impl
