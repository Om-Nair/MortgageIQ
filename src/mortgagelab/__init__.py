"""MortgageLab research package.

Stage 1 provides configuration and project boundaries only. It contains no
loan-level data parser, event mapping, empirical analysis, or model.
"""

from mortgagelab.config import ProjectConfig, load_project_config

__all__ = ["ProjectConfig", "load_project_config"]
__version__ = "0.1.0"
