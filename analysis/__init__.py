"""
Analysis Module
===============
Scripts for analyzing churn patterns and model validation.

Available scripts:
- validate_model: Check for data leakage, validate accuracy
- analyze_multi_factor: Multi-factor hypothesis testing
- analyze_geographic_channel: Geographic and channel analysis
- prove_state_hypothesis: Statistical significance tests

Usage:
    from analysis import validate_model
    # Or run directly: python -m analysis.validate_model
"""

__all__ = [
    "validate_model",
    "analyze_multi_factor", 
    "analyze_geographic_channel",
    "prove_state_hypothesis",
]
