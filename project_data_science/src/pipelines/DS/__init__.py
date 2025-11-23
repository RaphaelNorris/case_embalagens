"""
ml_pipeline package
===================

This package contains a modular implementation of the manufacturing analytics
pipeline built from the user‑provided notebooks.  The goal of the package is
to provide reusable components for loading raw data, performing feature
engineering, clustering product profiles, training a productivity classifier
and explaining model predictions using SHAP.  Everything is written as
functions with clear type hints, docstrings and minimal side effects.  You can
import individual functions or run the high level pipelines defined in
``pipelines.py``.

The package is intentionally generic and parameterised: it does not hard code
absolute file system locations or specific machine types.  Instead you pass
paths and options into the functions.  See the examples in ``pipelines.py``
for guidance on how to assemble the pieces for different machine types like
flexo and corte/vinco.
"""

from . import config
from . import data_processing
from . import feature_engineering
from . import clustering
from . import modeling
from . import explainability
from . import pipelines

__all__ = [
    "config",
    "data_processing",
    "feature_engineering",
    "clustering",
    "modeling",
    "explainability",
    "pipelines",
]