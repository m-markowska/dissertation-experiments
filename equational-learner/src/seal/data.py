"""Read and project feature data for the FxF and SEAL learning pipeline."""

from __future__ import annotations
import ast
import csv
import unicodedata as ud
from functools import lru_cache
from itertools import product
from typing import Any, Dict, List, Literal, Optional, Sequence, Set, Tuple



def _read_tsv(path: str) -> Tuple[List[str], List[str], List[List[str]]]:
    """Read a segment-by-feature inventory.

    Args:
        path: Path to the tab-separated inventory.

    Returns:
        Feature names, NFC-normalized segment labels, and a feature-major
        matrix. ``matrix[i][j]`` is feature ``i`` for segment ``j``.
    """
    with open(path, "r", newline="") as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r]

    if not rows:
        raise ValueError("Empty TSV")

    feats = [r[0] for r in rows[1:]]
    segs  = [ud.normalize("NFC", s) for s in rows[0][1:]]
    M     = [r[1:] for r in rows[1:]]
    return feats, segs, M


@lru_cache(maxsize=None)
def features(path: str) -> List[str]:
    """Read feature names in inventory row order.

    Args:
        path: Path to the tab-separated inventory.

    Returns:
        Feature names in the order used by prepared output strings.
    """
    feats, _, _ = _read_tsv(path)
    return feats


def feature_id(path: str) -> Dict[int, str]:
    """Index the inventory's feature names.

    Args:
        path: Path to the tab-separated inventory.

    Returns:
        Mapping from zero-based row index to feature name.
    """
    return {i: f for i, f in enumerate(features(path))}


def get_alphabet(
    path: str,
    type: Literal["segment", "feature"],
    features: Optional[List[str]] = None,
) -> List[str]:
    """Build a segment or projected-feature alphabet from an inventory.

    Args:
        path: Path to the tab-separated inventory.
        type: ``"segment"`` for header labels or ``"feature"`` for bundles.
        features: Ordered features to include in each bundle. ``None`` selects
            every inventory feature.

    Returns:
        Segment labels, or unique feature bundles in first-occurrence order.
    """
    feats, segs, M = _read_tsv(path)  # uses NFC-normalized header from our earlier helper

    if type == "segment":
        return list(segs)

    # type == "feature"
    if features is None:
        use_idx = list(range(len(feats)))
    else:
        name_to_idx = {f: i for i, f in enumerate(feats)}
        # print(name_to_idx)
        try:
            use_idx = [name_to_idx[name] for name in features]
        except KeyError as e:
            raise KeyError(f"Unknown feature '{e.args[0]}'. Available: {feats}")

    elements: List[str] = []
    seen = set()
    for j, _seg in enumerate(segs):
        element = "".join(M[i][j] for i in use_idx)
        if element not in seen:
            elements.append(element)
            seen.add(element)
    return elements


def transform_alphabet(alphabet: Sequence[str]) -> List[List[str]]:
    """Convert symbols to the representation used by the transducer.

    Args:
        alphabet: Non-boundary symbols.

    Returns:
        One-item symbol lists followed by left and right boundary markers.
    """

    new_alphabet = []
    for alpha in alphabet:
        new_alphabet.append([alpha])
    new_alphabet.append(['<'])
    new_alphabet.append(['>'])

    return new_alphabet


def extract_feat_pairs(
    features: Sequence[str],
    feature_ids: Dict[int, str],
    gen_pairs: Sequence[Sequence[Any]],
    k: Optional[int] = None,
) -> List[List[Any]]:
    """Project full-feature examples onto one learning specification.

    The first item in ``features`` is the predicted output feature. All listed
    features form each projected input symbol. Duplicate projected pairs are
    removed in first-occurrence order.

    Args:
        features: Ordered input features, beginning with the output target.
        feature_ids: Mapping from output-string index to feature name.
        gen_pairs: Full-feature input/output examples.
        k: Optional synthetic-sample length bound. Inputs longer than ``1`` for
            ``k=1`` or ``2k-1`` otherwise are omitted.

    Returns:
        Boundary-marked projected inputs paired with target-feature strings.
    """


    feat_data = []
    pred_feat_id = 0
    for key,v in feature_ids.items():
        if features[0] == v:
            pred_feat_id = key
    # print('pred_feat_id:', pred_feat_id)
    if len(features) == 1:
        feat_id = 0

        for key,v in feature_ids.items():
            if features[0] == v:
                feat_id = key
        feat_data = []           
        for pair in gen_pairs:
            # print('pair: ', pair)
            word_in = pair[0]
            word_out = pair[1]
            temp_feat_in = []
            temp_feat_out = []
            temp_feat_in.append(list(product(['<'], repeat=1))[0])
            for i in word_in:
                if i[0] == '>' or i[0] == '<':
                    continue
                else:
                    feat_in = i[0][feat_id]
                    temp_feat_in.append(list(product([feat_in], repeat=1))[0])
            temp_feat_in.append(list(product(['>'], repeat=1))[0])
            temp_feat_out = word_out[feat_id]
            # print('temp_feat_in: ', temp_feat_in)
            # print('temp_feat_out: ', temp_feat_out)
            feat_data.append([temp_feat_in, temp_feat_out])
    else:
        feat_id = []

        for feature in features:
            for key,v in feature_ids.items():
                if feature == v:
                    feat_id.append(key)


        for pair in gen_pairs:
            # print('pair: ', pair)
            word_in = pair[0]
            word_out = pair[1]

            # print('word out: ', word_out)
            temp_feats_in = []
            # temp_feats_out = []
            temp_feats_in.append(list(product(['<'], repeat=1))[0])
            for i in word_in:
                if i[0] == '>' or i[0] == '<':
                    continue
                else:
                    temp_bundle = ''
                    for f_id in feat_id:
                        temp_bundle += i[0][f_id]
                    temp_feats_in.append(list(product([temp_bundle], repeat=1))[0])
            temp_feats_in.append(list(product(['>'], repeat=1))[0])
            # for f_id in feat_id:
            #     temp_feats_out.append(word_out[f_id])
            temp_feats_out = word_out[pred_feat_id]
            # print('temp_feats_in: ', temp_feats_in)
            # print('temp feats out: ', temp_feats_out)
            feat_data.append([temp_feats_in, temp_feats_out])

    result = []
    for i in feat_data:
        if i not in result:
            result.append(i)
        else:
            continue
    # return result


    ######## -use below if learning from fake data- #########
    if k:
        updated_res = []
        # print(f'we got some k: {k} ')
        if k == 1:
            # print('k is actually 1')
            length = 1
        else:
            
            length = (2*k) -1
        # print(f'len: {length}')
        for pair in result:
            if len(pair[0])-2 <= length:
                # print(pair)
                updated_res.append(pair)
        return updated_res 
    else:
        return result


def read_org_data(file_path: str) -> List[Tuple[Any, ...]]:
    """Read prepared data whose TSV cells contain Python literals.

    Args:
        file_path: Path to a prepared feature-pair file.

    Returns:
        Parsed nonblank rows as tuples of literal values.
    """
    result: List[Tuple[Any, ...]] = []
    le = ast.literal_eval  # local binding for speed

    with open(file_path, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        # next(reader, None)  # skip header row, if present
        append = result.append  # local binding for speed

        for row in reader:
            if not row:
                continue
            # parse each cell as a literal, then pack into a tuple
            append(tuple(le(cell) for cell in row))

    return result


def map_Oi_to_outputs(
    trans_with_O: Sequence[Sequence[Any]],
    trans_no_O: Sequence[Sequence[Any]],
) -> Dict[str, Set[str]]:
    """Construct the identity output hypothesis for encoded transitions.

    Args:
        trans_with_O: Transitions whose output field contains an ``O`` label.
        trans_no_O: Structurally matching transitions with concrete outputs.

    Returns:
        Mapping from each ``O`` label to its singleton identity output set.
    """

    # Build a lookup: (prev, next) -> out_list
    lookup = {}
    for prev, nxt, out_list, out_sym in trans_no_O:
        lookup[(prev, nxt)] = out_list

    # Map each Oi to the matched out_list's first element (as a SET, like before)
    mapping = {}
    for prev, nxt, oi, out_sym in trans_with_O:
        try:
            mapping[oi] = {lookup[(prev, nxt)][0]}
        except KeyError as e:
            raise KeyError(f"No matching transition without O for ({prev!r}, {nxt!r})") from e

    return mapping
