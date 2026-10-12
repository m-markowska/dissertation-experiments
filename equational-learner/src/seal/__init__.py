"""Factor by Feature architecture with PRD-SEAL and LCD-SEAL learners."""

from .fxf import learn_fxf
from .learner import learn_lcd_seal, learn_prd_seal, learn_seal

__all__ = ["learn_fxf", "learn_seal", "learn_prd_seal", "learn_lcd_seal"]

# Import-compatible historical names. New documentation and wildcard imports
# expose only the dissertation terminology above.
from .equational import flex_learn, learn_one_feat
from .mappings import learn_kisl_dsf, learner_identity
