"""Fast file filtering with pattern matching."""

import fnmatch
from ..config import FilterConfig


class FastFileFilter:
    """Fast file filtering with pattern matching."""
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self._exclude_patterns = [p.lower() for p in config.exclude_patterns]
        self._include_patterns = [p.lower() for p in config.include_patterns]
    
    def should_process(self, file_path: str) -> bool:
        """Check if file should be processed."""
        path_lower = file_path.lower()
        
        # Check exclude patterns
        for pattern in self._exclude_patterns:
            if fnmatch.fnmatch(path_lower, pattern) or pattern in path_lower:
                return False
        
        # Check include patterns (if any)
        if self._include_patterns:
            return any(
                fnmatch.fnmatch(path_lower, p) or p in path_lower
                for p in self._include_patterns
            )
        
        return True
    
    def should_skip_function(self, line_count: int, is_private: bool = False, 
                            is_property: bool = False, is_accessor: bool = False) -> bool:
        """Check if function should be skipped."""
        if line_count < self.config.min_function_lines:
            return True
        if self.config.skip_private and is_private:
            return True
        if self.config.skip_properties and is_property:
            return True
        if self.config.skip_accessors and is_accessor:
            return True
        return False
