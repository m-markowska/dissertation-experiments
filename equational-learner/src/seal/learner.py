"""Public SEAL learner interface.

SEAL learns one feature-level transducer for a fixed target feature, input
feature projection, locality width, processing direction, and output-
distribution mode. Factor by Feature orchestration is exposed separately from
``seal.fxf``.
"""

from __future__ import annotations

from typing import Any

from .equational import _learn_seal_impl
from .mappings import learn_lcd_seal, learn_prd_seal

__all__ = ["learn_seal", "learn_prd_seal", "learn_lcd_seal"]


def learn_seal(
    features: list[str],
    sigma_inventory: str,
    delta_inventory: str,
    feature_data: str,
    k: int,
    *,
    direction: str = "L2R",
    check_training: bool = True,
    mode: str = "lcd-seal",
    learner: Any = None,
) -> tuple[Any, Any]:
    """Learn one fixed-parameter feature-level transducer with SEAL.

    Args:
        features: Input projection ``Phi``, beginning with target feature
            ``phi``.
        sigma_inventory: Input segment-feature inventory path.
        delta_inventory: Output segment-feature inventory path.
        feature_data: Feature-encoded input/output training-pair path.
        k: Locality width used to construct the transducer skeleton.
        direction: Processing direction label, normally ``L2R`` or ``R2L``.
        check_training: Whether to evaluate the learned transducer on training
            pairs.
        mode: Output-distribution mode, ``prd-seal`` or ``lcd-seal``.
        learner: Deprecated compatibility spelling for ``mode``.

    Returns:
        A status and diagnostic mapping containing the learned feature-level
        transducer or failure information.
    """
    return _learn_seal_impl(
        features,
        sigma_inventory,
        delta_inventory,
        feature_data,
        k,
        direction=direction,
        check_training=check_training,
        mode=mode,
        learner=learner,
    )
