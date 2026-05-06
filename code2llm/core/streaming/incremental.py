"""Incremental analysis with change detection."""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from code2llm.core.config import Config, FAST_CONFIG


class StreamingIncrementalAnalyzer:
    """Incremental analysis with change detection for streaming analyzer."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or FAST_CONFIG
        self.state_file = Path(".code2llm_state.json")
        self.previous_state: Dict[str, str] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load previous analysis state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.previous_state = data.get('file_hashes', {})
            except Exception:
                pass

    def _save_state(self, current_state: Dict[str, str]) -> None:
        """Save current analysis state."""
        with open(self.state_file, 'w') as f:
            json.dump({
                'file_hashes': current_state,
                'timestamp': time.time()
            }, f)

    def get_changed_files(
        self,
        project_path: Path
    ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """Get changed and unchanged files."""
        changed = []
        unchanged = []
        current_state = {}

        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_bytes()
                file_hash = hashlib.md5(content).hexdigest()
                file_str = str(py_file)

                current_state[file_str] = file_hash

                if file_str in self.previous_state:
                    if self.previous_state[file_str] == file_hash:
                        unchanged.append((file_str, self._get_module_name(py_file, project_path)))
                    else:
                        changed.append((file_str, self._get_module_name(py_file, project_path)))
                else:
                    changed.append((file_str, self._get_module_name(py_file, project_path)))
            except Exception:
                pass

        self._save_state(current_state)
        return changed, unchanged

    def _get_module_name(self, py_file: Path, project_path: Path) -> str:
        """Calculate module name."""
        rel_path = py_file.relative_to(project_path)
        parts = list(rel_path.parts)[:-1]
        if py_file.name == '__init__.py':
            return '.'.join(parts) if parts else project_path.name
        return '.'.join(parts + [py_file.stem])
