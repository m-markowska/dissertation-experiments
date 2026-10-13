"""Load dataset and feature-projection settings for experiment runners."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ExperimentSpec:
    """Dataset paths and named feature projections for one experiment."""

    pairs: Path
    inventory: Path
    configurations: dict[str, list[str]]


def load_experiment_spec(path: Path) -> ExperimentSpec:
    """Read and validate an experiment configuration.

    Relative dataset paths are resolved from the directory containing the
    configuration file.

    Args:
        path: JSON file containing ``pairs``, ``inventory``, and a mapping of
            named ``configurations`` to ordered feature lists.

    Returns:
        Validated dataset paths and feature projections.

    Raises:
        ValueError: If a required field is absent or has an invalid shape.
    """
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise ValueError("The experiment configuration must be a JSON object.")
    pairs = content.get("pairs")
    inventory = content.get("inventory")
    configurations = content.get("configurations")
    if not isinstance(pairs, str) or not isinstance(inventory, str):
        raise ValueError("The pairs and inventory fields must be path strings.")
    if not isinstance(configurations, dict) or not configurations:
        raise ValueError("The configurations field must be a nonempty object.")

    validated: dict[str, list[str]] = {}
    for name, features in configurations.items():
        if not isinstance(name, str) or not name:
            raise ValueError("Every configuration must have a nonempty name.")
        if (
            not isinstance(features, list)
            or not features
            or not all(isinstance(feature, str) and feature for feature in features)
        ):
            raise ValueError(
                f"Configuration {name!r} must contain a nonempty feature list."
            )
        validated[name] = features

    base = path.parent
    return ExperimentSpec(
        pairs=base / pairs,
        inventory=base / inventory,
        configurations=validated,
    )


def select_configurations(
    spec: ExperimentSpec,
    targets: list[str] | None,
) -> list[str]:
    """Select configured experiment names while preserving their order.

    Args:
        spec: Loaded experiment specification.
        targets: Requested names, or ``None`` to select every configuration.

    Returns:
        Requested names in command-line or configuration-file order.

    Raises:
        ValueError: If a requested name is absent from the configuration.
    """
    selected = targets or list(spec.configurations)
    unknown = [name for name in selected if name not in spec.configurations]
    if unknown:
        available = ", ".join(spec.configurations)
        raise ValueError(
            f"Unknown configuration(s): {', '.join(unknown)}. Available: {available}."
        )
    return selected
