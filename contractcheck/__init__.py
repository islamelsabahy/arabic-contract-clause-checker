"""Rule-based first-pass review of Arabic real estate contracts. Not legal advice."""
from .checker import Finding, Report, analyze, normalize

__all__ = ["Finding", "Report", "analyze", "normalize"]
__version__ = "0.2.0"
