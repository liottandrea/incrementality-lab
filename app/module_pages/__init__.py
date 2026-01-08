"""
Module Pages Package
Contains separate modules for each panel of the Streamlit app
"""

from . import generate_data
from . import eda
from . import validate_quality
from . import model_setup
from . import results
from . import roi_insights
from . import export

__all__ = [
    'generate_data',
    'eda',
    'validate_quality',
    'model_setup',
    'results',
    'roi_insights',
    'export'
]
