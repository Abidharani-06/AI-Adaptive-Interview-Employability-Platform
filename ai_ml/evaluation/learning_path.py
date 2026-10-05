"""
Evaluation Learning Path Bridge
-------------------------------
Provides transparent backwards compatibility by exposing LearningPathGenerator
from the primary recomendation module.
"""

import sys
from pathlib import Path

# Resolve path to recomendation module
rec_dir = Path(__file__).resolve().parents[1] / "recomendation"
if str(rec_dir) not in sys.path:
    sys.path.append(str(rec_dir))

from learning_path import LearningPathGenerator, CURRICULUM_DATABASE

__all__ = ["LearningPathGenerator", "CURRICULUM_DATABASE"]
