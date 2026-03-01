"""Smart file prioritization for optimal analysis order."""

import ast
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .strategies import ScanStrategy


@dataclass
class FilePriority:
    """Priority scoring for file analysis order."""
    file_path: str
    module_name: str
    priority_score: float
    reasons: List[str] = field(default_factory=list)
    
    # Priority factors
    is_entry_point: bool = False
    is_public_api: bool = False
    has_main: bool = False
    import_count: int = 0
    lines_of_code: int = 0


class SmartPrioritizer:
    """Smart file prioritization for optimal analysis order."""
    
    def __init__(self, strategy: ScanStrategy):
        self.strategy = strategy
    
    def prioritize_files(
        self,
        files: List[Tuple[str, str]],
        project_path: Path
    ) -> List[FilePriority]:
        """Score and sort files by importance."""
        scored = []
        
        # First pass: gather import relationships
        import_graph = self._build_import_graph(files)
        
        for file_path, module_name in files:
            score = 0.0
            reasons = []
            
            # Check if has main
            has_main = self._check_has_main(file_path)
            if has_main:
                score += 100.0
                reasons.append("has_main")
            
            # Check if entry point (not imported by others)
            is_entry = module_name not in import_graph or len(import_graph[module_name]) == 0
            if is_entry:
                score += 50.0
                reasons.append("entry_point")
            
            # Check if public API (no underscore prefix)
            is_public = not any(part.startswith('_') for part in module_name.split('.'))
            if is_public:
                score += 20.0
                reasons.append("public_api")
            
            # Import count (more imports = more central)
            import_count = len(import_graph.get(module_name, []))
            score += import_count * 5.0
            
            # File size (prefer smaller files first for quick wins)
            try:
                loc = len(Path(file_path).read_text().split('\n'))
                if loc < 100:
                    score += 10.0
                    reasons.append("small_file")
            except Exception:
                loc = 0
            
            priority = FilePriority(
                file_path=file_path,
                module_name=module_name,
                priority_score=score,
                reasons=reasons,
                is_entry_point=is_entry,
                is_public_api=is_public,
                has_main=has_main,
                import_count=import_count,
                lines_of_code=loc
            )
            scored.append(priority)
        
        # Sort by score descending
        scored.sort(key=lambda x: x.priority_score, reverse=True)
        return scored
    
    def _build_import_graph(
        self,
        files: List[Tuple[str, str]],
    ) -> Dict[str, Set[str]]:
        """Build import dependency graph."""
        # Map module names to who imports them
        imported_by: Dict[str, Set[str]] = defaultdict(set)
        
        for file_path, module_name in files:
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Simplified - just record the top-level module
                            top_module = alias.name.split('.')[0]
                            imported_by[top_module].add(module_name)
                    
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        top_module = node.module.split('.')[0]
                        imported_by[top_module].add(module_name)
            except Exception:
                pass
        
        return imported_by
    
    def _check_has_main(self, file_path: str) -> bool:
        """Check if file has if __name__ == "__main__" block."""
        try:
            content = Path(file_path).read_text()
            return 'if __name__' in content and '__main__' in content
        except Exception:
            return False
