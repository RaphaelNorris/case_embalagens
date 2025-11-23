"""
Thin wrapper that exposes the high-level inference helpers so that notebooks
can simply ``import inference`` and access ``predict_orders`` without knowing
the internal package structure.
"""

from pipelines.DS.inference import predict_orders

__all__ = ["predict_orders"]
