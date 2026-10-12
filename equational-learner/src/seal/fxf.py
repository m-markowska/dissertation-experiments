"""Learner-agnostic Factor by Feature (FxF) architecture.

FxF decomposes a segmental transduction into feature-level transducers
``tau(Phi, phi)``. The architecture does not prescribe the algorithm that
learns each transducer: callers may supply any compatible ``feature_learner``
to :func:`learn_fxf`. SEAL is the default learner in this package and in the
reported dissertation experiments.
"""

from __future__ import annotations

from pprint import pprint
from typing import Any

from .equational import iter_candidates_by_num_states
from .learner import learn_seal
from .preprocessing import features as inventory_features

__all__ = ["learn_fxf"]


def learn_fxf(
    sigma_inventory: str,
    delta_inventory: str,
    feature_data: str,
    *,
    reversed_feature_data: str | None = None,
    require_both: bool = True,
    base_features: list[str] | None = None,
    verbose_search: bool = False,
    k_min: int = 1,
    k_max: int = 4,
    l_max: int = 5,
    check_training: bool = True,
    print_learned_transitions: bool = True,
    mode: str = "lcd-seal",
    feature_learner: Any = learn_seal,
    preferred_direction: str = "R2L",
) -> Any:
    """Apply FxF with any compatible feature-level learner.

    Args:
        sigma_inventory: Input segment-feature inventory path.
        delta_inventory: Output segment-feature inventory path.
        feature_data: Left-to-right feature-encoded training-pair path.
        reversed_feature_data: Optional right-to-left training-pair path.
        require_both: Whether available directions must both succeed.
        base_features: Target output features; defaults to all inventory
            features.
        verbose_search: Whether to print candidate-search diagnostics.
        k_min: Smallest locality width considered.
        k_max: Largest locality width considered.
        l_max: Largest input feature-set size considered.
        check_training: Whether the feature learner checks its training pairs.
        print_learned_transitions: Whether to print successful transitions.
        mode: Learner-specific mode forwarded unchanged to
            ``feature_learner``.
        feature_learner: Callable that learns one feature-level transducer.
            SEAL is the default; another learner may be supplied through an
            adapter with the same call signature.
        preferred_direction: Direction evaluated first, ``L2R`` or ``R2L``.

    Returns:
        Per-target-feature winners and candidates tested by the FxF search.
    """
    if preferred_direction not in {"L2R", "R2L"}:
        raise ValueError("preferred_direction must be 'L2R' or 'R2L'")
    if k_min < 1 or k_max < k_min:
        raise ValueError("FxF requires 1 <= k_min <= k_max")
    if l_max < 1:
        raise ValueError("l_max must be at least 1")

    available_features = inventory_features(sigma_inventory)
    targets = list(base_features) if base_features is not None else list(available_features)
    unknown_targets = [target for target in targets if target not in available_features]
    if unknown_targets:
        raise ValueError(f"Target features absent from inventory: {unknown_targets}")

    directional_data = {"L2R": feature_data}
    if reversed_feature_data is not None:
        directional_data["R2L"] = reversed_feature_data
    directions = sorted(
        directional_data,
        key=lambda direction: (direction != preferred_direction, direction),
    )

    final_result: dict[tuple[str], dict[str, Any]] = {}
    for target in targets:
        tested_in_order = []
        winner = None
        candidates = iter_candidates_by_num_states(
            [target],
            available_features,
            sigma_inventory=sigma_inventory,
            k_min=k_min,
            k_max=k_max,
            l_max=min(l_max, len(available_features)),
        )
        for projection, k, state_count in candidates:
            outcomes = {}
            for direction in directions:
                status, details = feature_learner(
                    projection,
                    sigma_inventory,
                    delta_inventory,
                    directional_data[direction],
                    k,
                    direction=direction,
                    check_training=check_training,
                    mode=mode,
                )
                outcomes[direction] = (status, details)
                if not require_both and status == "passed":
                    break

            passed = [status == "passed" for status, _details in outcomes.values()]
            passed_any = any(passed)
            passed_all_available = len(outcomes) == len(directions) and all(passed)
            candidate_passed = passed_all_available if require_both else passed_any
            record = {
                "feat": projection,
                "feat_k": k,
                "states": state_count,
                "outcome": {
                    "status": "passed" if candidate_passed else "failed",
                    "passed_any": passed_any,
                    "passed_both": len(directions) == 2 and passed_all_available,
                    "outcomes": outcomes,
                },
            }
            tested_in_order.append(record)

            if verbose_search:
                print(
                    f"target={target} features={projection} k={k} "
                    f"states={state_count} status={record['outcome']['status']}"
                )
            if not candidate_passed:
                continue

            winner = record
            if print_learned_transitions:
                for direction, (status, details) in outcomes.items():
                    if status != "passed" or not isinstance(details, dict):
                        continue
                    print(
                        f"[{direction}] target={target} features={projection} "
                        f"k={k} mode={mode}"
                    )
                    pprint(details.get("learned_transitions"))
            break

        final_result[(target,)] = {
            "result": "passed" if winner is not None else False,
            "winner": winner,
            "tested_in_order": tested_in_order,
        }
    return final_result
