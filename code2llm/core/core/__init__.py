"""Core modules split from analyzer.py."""

from .file_cache import FileCache
from .file_filter import FastFileFilter
from .file_analyzer import FileAnalyzer, _analyze_single_file
from .refactoring import RefactoringAnalyzer
