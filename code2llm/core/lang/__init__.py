"""Language-specific analyzers for non-Python source files.

Provides:
  - LanguageParser ABC — abstract base class for all language parsers
  - LANGUAGE_REGISTRY — dict mapping extensions to parser functions
  - register_language — decorator for auto-registration
  - get_parser(extension) — lookup parser by file extension
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Set, Optional
from pathlib import Path

from code2llm.core.models import ModuleInfo, FunctionInfo, ClassInfo


# Type alias for parser results
ParserResult = Dict[str, Any]


class LanguageParser(ABC):
    """Abstract base class for language-specific parsers.

    All language parsers must inherit from this class and implement:
      - analyze() method to parse file content
      - supported_extensions class attribute

    Example:
        @register_language('.go', '.golang')
        class GoParser(LanguageParser):
            supported_extensions = ('.go', '.golang')

            def analyze(self, content, file_path, module_name, stats):
                # Parse Go code
                return {'module': ..., 'functions': ..., 'classes': ...}
    """

    supported_extensions: tuple = ()
    language_name: str = ""

    @abstractmethod
    def analyze(
        self,
        content: str,
        file_path: str,
        module_name: str,
        stats: Dict[str, Any]
    ) -> ParserResult:
        """Analyze file content and return parsed structure.

        Args:
            content: File content as string
            file_path: Absolute path to file
            module_name: Logical module name
            stats: Statistics dict to update

        Returns:
            Dict with 'module', 'functions', 'classes', 'nodes', 'edges'
        """
        pass

    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions


# Legacy parser function type
LegacyParser = Callable[[str, str, str, str, Dict[str, Any]], ParserResult]


# Registry: extension -> parser instance or function
LANGUAGE_REGISTRY: Dict[str, Any] = {}


def register_language(*extensions: str, name: str = ""):
    """Decorator to register a language parser.

    Args:
        *extensions: File extensions this parser handles (e.g., '.go', '.rs')
        name: Human-readable language name

    Example:
        @register_language('.go', '.golang', name='Go')
        class GoParser(LanguageParser):
            ...

        @register_language('.rb', name='Ruby')
        def analyze_ruby(content, file_path, module_name, ext, stats):
            ...
    """
    def decorator(cls_or_func):
        if isinstance(cls_or_func, type) and issubclass(cls_or_func, LanguageParser):
            # It's a class
            parser = cls_or_func()
            parser.language_name = name or cls_or_func.__name__.replace('Parser', '')
            for ext in extensions:
                LANGUAGE_REGISTRY[ext.lower()] = parser
        else:
            # It's a function
            for ext in extensions:
                LANGUAGE_REGISTRY[ext.lower()] = cls_or_func
        return cls_or_func
    return decorator


def get_parser(extension: str) -> Optional[Any]:
    """Get parser for a file extension.

    Args:
        extension: File extension (e.g., '.go', '.rs')

    Returns:
        LanguageParser instance or legacy function, or None if not found
    """
    return LANGUAGE_REGISTRY.get(extension.lower())


def list_parsers() -> Dict[str, Any]:
    """List all registered parsers."""
    return dict(LANGUAGE_REGISTRY)


# Legacy function imports (for backward compatibility)
from .typescript import analyze_typescript_js
from .go_lang import analyze_go
from .rust import analyze_rust
from .java import analyze_java
from .cpp import analyze_cpp
from .csharp import analyze_csharp
from .php import analyze_php
from .ruby import analyze_ruby
from .generic import analyze_generic


# Register legacy parsers
register_language('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs')(analyze_typescript_js)
register_language('.go')(analyze_go)
register_language('.rs')(analyze_rust)
register_language('.java')(analyze_java)
register_language('.cpp', '.cc', '.cxx', '.hpp', '.h', '.c')(analyze_cpp)
register_language('.cs')(analyze_csharp)
register_language('.php')(analyze_php)

# Import and register RubyParser class (demonstrating new ABC pattern)
from .ruby import RubyParser
LANGUAGE_REGISTRY['.rb'] = RubyParser()
LANGUAGE_REGISTRY['.rbw'] = RubyParser()

# Generic parser as fallback for unknown extensions
LANGUAGE_REGISTRY['*'] = analyze_generic


__all__ = [
    'LanguageParser',
    'ParserResult',
    'register_language',
    'LANGUAGE_REGISTRY',
    'get_parser',
    'list_parsers',
    # New class-based parsers
    'RubyParser',
    # Legacy exports
    'analyze_typescript_js',
    'analyze_go',
    'analyze_rust',
    'analyze_java',
    'analyze_cpp',
    'analyze_csharp',
    'analyze_php',
    'analyze_ruby',
    'analyze_generic',
]
