"""Mermaid Exporter for code2llm.

Three distinct outputs:
  - export()           → flow.mmd   — full call graph with CC-based styling
  - export_call_graph() → calls.mmd  — simplified call graph (edges only, no isolates)
  - export_compact()    → compact_flow.mmd — module-level aggregation
  
New 3-level flow diagrams (Plan R1):
  - export_flow_compact()   → flow.mmd — architectural view (~50 nodes)
  - export_flow_detailed()  → flow_detailed.mmd — per-module view (~150 nodes)
  - export_flow_full()      → flow_full.mmd — full debug view (all nodes)
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from .base import Exporter
from code2llm.core.models import AnalysisResult


class MermaidExporter(Exporter):
    """Export call graph to Mermaid format."""

    # ------------------------------------------------------------------ #
    # 1. flow.mmd — full graph with CC styling
    # ------------------------------------------------------------------ #
    def export(self, result: AnalysisResult, output_path: str) -> None:
        """Export full flow diagram with CC-based node shapes and styling."""
        lines = ["flowchart TD"]

        # Subgraphs per module
        self._render_subgraphs(result, lines)

        # Edges — all cross-function calls
        self._render_edges(result, lines, limit=600)

        # CC-based styling
        self._render_cc_styles(result, lines)

        self._write(output_path, lines)

    def _render_subgraphs(self, result: AnalysisResult, lines: List[str]) -> None:
        """Render module subgraphs with CC-shaped nodes."""
        modules: Dict[str, list] = {}
        for func_name, fi in result.functions.items():
            module = self._module_of(func_name)
            modules.setdefault(module, []).append((func_name, fi))

        for module, funcs in sorted(modules.items()):
            safe_module = self._safe_module(module)
            lines.append(f"    subgraph {safe_module}")
            for func_name, fi in funcs[:60]:
                sid = self._readable_id(func_name)
                short = fi.name[:35]
                cc = self._get_cc(fi)
                if cc >= 15:
                    lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
                elif cc >= 8:
                    lines.append(f'        {sid}("{short} CC={cc}")')
                else:
                    lines.append(f'        {sid}["{short}"]')
            lines.append("    end")

    def _render_edges(self, result: AnalysisResult, lines: List[str], limit: int = 600) -> None:
        """Render cross-function call edges up to limit."""
        seen_edges: Set[Tuple[str, str]] = set()
        for func_name, fi in result.functions.items():
            src = self._readable_id(func_name)
            for callee in fi.calls[:15]:
                resolved = self._resolve(callee, result.functions)
                if resolved and resolved != func_name:
                    dst = self._readable_id(resolved)
                    edge = (src, dst)
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        lines.append(f"    {src} --> {dst}")
                        if len(seen_edges) >= limit:
                            return
            if len(seen_edges) >= limit:
                return

    def _render_cc_styles(self, result: AnalysisResult, lines: List[str]) -> None:
        """Add CC-based class styling for high/medium complexity nodes."""
        lines.append("")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        high_nodes = []
        med_nodes = []
        for func_name, fi in result.functions.items():
            cc = self._get_cc(fi)
            sid = self._readable_id(func_name)
            if cc >= 15:
                high_nodes.append(sid)
            elif cc >= 8:
                med_nodes.append(sid)
        if high_nodes:
            lines.append(f"    class {','.join(high_nodes[:30])} highCC")
        if med_nodes:
            lines.append(f"    class {','.join(med_nodes[:30])} medCC")

    @staticmethod
    def _get_cc(fi) -> int:
        """Extract cyclomatic complexity from FunctionInfo."""
        if isinstance(fi.complexity, dict):
            return fi.complexity.get('cyclomatic_complexity', 0)
        return fi.complexity or 0

    # ------------------------------------------------------------------ #
    # 2. calls.mmd — edges only, no isolated nodes
    # ------------------------------------------------------------------ #
    def export_call_graph(self, result: AnalysisResult, output_path: str) -> None:
        """Export simplified call graph — only connected nodes."""
        lines = ["flowchart LR"]

        # Collect connected nodes first
        connected: Set[str] = set()
        edges: List[Tuple[str, str]] = []
        for func_name, fi in result.functions.items():
            for callee in fi.calls[:10]:
                resolved = self._resolve(callee, result.functions)
                if resolved and resolved != func_name:
                    connected.add(func_name)
                    connected.add(resolved)
                    edges.append((func_name, resolved))
                    if len(edges) >= 500:
                        break
            if len(edges) >= 500:
                break

        # Group connected nodes by module
        modules: Dict[str, list] = {}
        for fn in connected:
            module = self._module_of(fn)
            fi = result.functions.get(fn)
            if fi:
                modules.setdefault(module, []).append((fn, fi))

        for module, funcs in sorted(modules.items()):
            safe_module = self._safe_module(module)
            lines.append(f"    subgraph {safe_module}")
            for func_name, fi in funcs:
                sid = self._readable_id(func_name)
                short = fi.name[:30]
                lines.append(f'        {sid}["{short}"]')
            lines.append("    end")

        # Edges
        seen: Set[Tuple[str, str]] = set()
        for src, dst in edges:
            pair = (self._readable_id(src), self._readable_id(dst))
            if pair not in seen:
                seen.add(pair)
                lines.append(f"    {pair[0]} --> {pair[1]}")

        self._write(output_path, lines)

    # ------------------------------------------------------------------ #
    # 3. compact_flow.mmd — module-level aggregation
    # ------------------------------------------------------------------ #
    def export_compact(self, result: AnalysisResult, output_path: str) -> None:
        """Export module-level graph: one node per module, weighted edges."""
        lines = ["flowchart TD"]

        # Compute module stats
        mod_funcs: Dict[str, int] = defaultdict(int)
        mod_lines: Dict[str, int] = defaultdict(int)
        for func_name, fi in result.functions.items():
            module = self._module_of(func_name)
            mod_funcs[module] += 1
            mod_lines[module] += fi.end_line - fi.line if hasattr(fi, 'end_line') and fi.end_line else 0

        # Cross-module edges with weights
        cross_edges: Dict[Tuple[str, str], int] = defaultdict(int)
        for func_name, fi in result.functions.items():
            src_mod = self._module_of(func_name)
            for callee in fi.calls:
                resolved = self._resolve(callee, result.functions)
                if resolved:
                    dst_mod = self._module_of(resolved)
                    if dst_mod != src_mod:
                        cross_edges[(src_mod, dst_mod)] += 1

        # Only modules with cross-edges
        active_mods: Set[str] = set()
        for (s, d) in cross_edges:
            active_mods.add(s)
            active_mods.add(d)

        # Add all modules with functions as fallback
        if not active_mods:
            active_mods = set(mod_funcs.keys())

        # Nodes — module boxes
        for mod in sorted(active_mods):
            sid = self._safe_module(mod)
            nf = mod_funcs.get(mod, 0)
            lines.append(f'    {sid}["{mod}<br/>{nf} funcs"]')

        # Weighted edges
        for (src, dst), weight in sorted(cross_edges.items(), key=lambda x: -x[1]):
            s = self._safe_module(src)
            d = self._safe_module(dst)
            if weight > 3:
                lines.append(f"    {s} ==>|{weight}| {d}")
            else:
                lines.append(f"    {s} -->|{weight}| {d}")

        self._write(output_path, lines)

    # ------------------------------------------------------------------ #
    # 4. NEW 3-level flow diagrams (Plan R1)
    # ------------------------------------------------------------------ #

    # Default skip patterns for noise reduction
    SKIP_PATTERNS = ('examples', 'benchmarks', 'demo_langs', 'tests', 'scripts')

    def _should_skip_module(self, module: str, include_examples: bool = False) -> bool:
        """Check if module should be skipped (examples, benchmarks, etc.)."""
        if include_examples:
            return False
        mod_lower = module.lower()
        return any(pat in mod_lower for pat in self.SKIP_PATTERNS)

    def _is_entry_point(self, func_name: str, fi, result: AnalysisResult) -> bool:
        """Detect if function is an entry point (main, cli, api entry)."""
        name = fi.name
        # Common entry point patterns
        if name in ('main', 'cli_main', 'run', 'start', 'serve'):
            return True
        if name.startswith('main_') or name.endswith('_main'):
            return True
        # CLI commands
        if 'cli' in func_name.lower() and name not in ('__init__', 'create_parser'):
            return True
        # API handlers
        if func_name.startswith('code2llm.api.'):
            return True
        # Entry points have no incoming calls from within the project
        has_incoming = any(func_name in (c.calls if hasattr(c, 'calls') else []) 
                          for c in result.functions.values())
        if not has_incoming and name not in ('__init__', '__getattr__'):
            return True
        return False

    def _find_critical_path(self, result: AnalysisResult, entry_points: List[str]) -> Set[str]:
        """Find the longest path from entry points (critical path)."""
        if not entry_points:
            return set()
        
        # Build reverse graph (who calls whom)
        callers: Dict[str, Set[str]] = defaultdict(set)
        for func_name, fi in result.functions.items():
            for callee in fi.calls:
                resolved = self._resolve(callee, result.functions)
                if resolved:
                    callers[resolved].add(func_name)
        
        # Find leaf nodes (functions that don't call anything)
        leaves = set()
        for func_name, fi in result.functions.items():
            has_internal_call = any(
                self._resolve(c, result.functions) for c in fi.calls
            )
            if not has_internal_call:
                leaves.add(func_name)
        
        # Find longest path from each entry point
        critical_nodes: Set[str] = set()
        
        def longest_path_dfs(start: str, visited: Set[str]) -> List[str]:
            """DFS to find longest path from start."""
            if start in visited:
                return []
            visited = visited | {start}
            fi = result.functions.get(start)
            if not fi:
                return [start]
            
            longest: List[str] = []
            for callee in fi.calls:
                resolved = self._resolve(callee, result.functions)
                if resolved and resolved not in visited:
                    path = longest_path_dfs(resolved, visited)
                    if len(path) > len(longest):
                        longest = path
            
            return [start] + longest
        
        # From each entry point, find longest path
        max_path: List[str] = []
        for ep in entry_points:
            if ep in result.functions:
                path = longest_path_dfs(ep, set())
                if len(path) > len(max_path):
                    max_path = path
        
        return set(max_path)

    def export_flow_compact(self, result: AnalysisResult, output_path: str,
                           include_examples: bool = False) -> None:
        """Export compact architectural view (~50 nodes).
        
        Shows entry points, high-level modules, and critical path.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Entry points (blue)")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        
        # Filter functions
        filtered_funcs = {
            name: fi for name, fi in result.functions.items()
            if not self._should_skip_module(self._module_of(name), include_examples)
        }
        
        # Identify entry points
        entry_points = [
            name for name, fi in filtered_funcs.items()
            if self._is_entry_point(name, fi, result)
        ]
        
        # Critical path (longest chain from entry)
        critical_path = self._find_critical_path(result, entry_points)
        
        # Top-level architecture nodes (CLI, Core, Exporters)
        arch_modules: Dict[str, List[str]] = {
            'CLI': [],
            'Core': [],
            'Exporters': [],
        }
        
        for func_name in filtered_funcs:
            module = self._module_of(func_name)
            if 'cli' in module.lower():
                arch_modules['CLI'].append(func_name)
            elif 'exporter' in module.lower() or 'export' in func_name.lower():
                arch_modules['Exporters'].append(func_name)
            else:
                arch_modules['Core'].append(func_name)
        
        # Render architecture subgraphs with key functions only
        for arch_name, funcs in arch_modules.items():
            if not funcs:
                continue
            lines.append(f"    subgraph {arch_name}")
            
            # Pick key functions: entry points + high CC + key pipeline functions
            key_funcs = []
            for fn in funcs:
                fi = filtered_funcs.get(fn)
                if not fi:
                    continue
                cc = self._get_cc(fi)
                is_entry = fn in entry_points
                is_critical = fn in critical_path
                
                if is_entry or is_critical or cc >= 15:
                    key_funcs.append(fn)
            
            # Limit to avoid clutter
            shown_funcs = key_funcs[:15]
            for func_name in shown_funcs:
                fi = filtered_funcs[func_name]
                sid = self._readable_id(func_name)
                short = fi.name[:30]
                cc = self._get_cc(fi)
                
                if func_name in entry_points:
                    lines.append(f'        {sid}["{short}"]')
                elif cc >= 15:
                    lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
                elif cc >= 8:
                    lines.append(f'        {sid}("{short} CC={cc}")')
                else:
                    lines.append(f'        {sid}["{short}"]')
            
            if len(key_funcs) > 15:
                lines.append(f'        ...["+{len(key_funcs) - 15} more"]')
            lines.append("    end")
            lines.append("")
        
        # Entry point styling
        if entry_points:
            entry_ids = [self._readable_id(ep) for ep in entry_points[:10]]
            lines.append(f"    class {','.join(entry_ids)} entry")
        
        self._write(output_path, lines)

    def export_flow_detailed(self, result: AnalysisResult, output_path: str,
                            include_examples: bool = False) -> None:
        """Export detailed per-module view (~150 nodes).
        
        Shows all significant functions per module with CC annotations.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Styling definitions")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        
        # Filter functions
        filtered_funcs = {
            name: fi for name, fi in result.functions.items()
            if not self._should_skip_module(self._module_of(name), include_examples)
        }
        
        # Identify entry points
        entry_points = [
            name for name, fi in filtered_funcs.items()
            if self._is_entry_point(name, fi, result)
        ]
        
        # Group by module (2 levels deep)
        modules: Dict[str, List[Tuple[str, Any]]] = defaultdict(list)
        for name, fi in filtered_funcs.items():
            mod = self._module_of(name)
            modules[mod].append((name, fi))
        
        # Render subgraphs per module
        for mod, funcs in sorted(modules.items()):
            safe_mod = self._safe_module(mod)
            lines.append(f"    subgraph {safe_mod}")
            
            # Sort by CC descending, then by name
            funcs_sorted = sorted(
                funcs,
                key=lambda x: (-self._get_cc(x[1]), x[1].name)
            )[:40]  # Max 40 per module
            
            for func_name, fi in funcs_sorted:
                sid = self._readable_id(func_name)
                short = fi.name[:35]
                cc = self._get_cc(fi)
                
                if cc >= 15:
                    lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
                elif cc >= 8:
                    lines.append(f'        {sid}("{short} CC={cc}")')
                else:
                    lines.append(f'        {sid}["{short}"]')
            
            if len(funcs) > 40:
                lines.append(f'        ...["+{len(funcs) - 40} more"]')
            lines.append("    end")
            lines.append("")
        
        # Render edges (limit to avoid chaos)
        seen_edges: Set[Tuple[str, str]] = set()
        edge_count = 0
        max_edges = 200
        
        for func_name, fi in filtered_funcs.items():
            src = self._readable_id(func_name)
            for callee in fi.calls[:10]:  # Limit calls per function
                resolved = self._resolve(callee, filtered_funcs)
                if resolved and resolved != func_name:
                    dst = self._readable_id(resolved)
                    edge = (src, dst)
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        lines.append(f"    {src} --> {dst}")
                        edge_count += 1
                        if edge_count >= max_edges:
                            break
            if edge_count >= max_edges:
                break
        
        # Apply styling
        high_nodes = []
        med_nodes = []
        for func_name, fi in filtered_funcs.items():
            cc = self._get_cc(fi)
            sid = self._readable_id(func_name)
            if cc >= 15:
                high_nodes.append(sid)
            elif cc >= 8:
                med_nodes.append(sid)
        
        if high_nodes:
            lines.append(f"    class {','.join(high_nodes[:30])} highCC")
        if med_nodes:
            lines.append(f"    class {','.join(med_nodes[:30])} medCC")
        if entry_points:
            entry_ids = [self._readable_id(ep) for ep in entry_points[:10]]
            lines.append(f"    class {','.join(entry_ids)} entry")
        
        self._write(output_path, lines)

    def export_flow_full(self, result: AnalysisResult, output_path: str,
                        include_examples: bool = False) -> None:
        """Export full debug view with all nodes (original flow.mmd).
        
        This is the original export() behavior with optional filtering.
        """
        lines = ["flowchart TD"]
        lines.append("")
        lines.append("    %% Styling definitions")
        lines.append("    classDef highCC fill:#ff6b6b,stroke:#c92a2a,color:#fff")
        lines.append("    classDef medCC fill:#ffd43b,stroke:#f08c00,color:#000")
        lines.append("    classDef entry fill:#4dabf7,stroke:#1971c2,color:#fff")
        lines.append("")
        
        # Filter functions if requested
        filtered_funcs = result.functions
        if not include_examples:
            filtered_funcs = {
                name: fi for name, fi in result.functions.items()
                if not self._should_skip_module(self._module_of(name), include_examples)
            }
        
        # Identify entry points
        entry_points = [
            name for name, fi in filtered_funcs.items()
            if self._is_entry_point(name, fi, result)
        ]
        
        # Subgraphs per module
        modules: Dict[str, list] = {}
        for func_name, fi in filtered_funcs.items():
            module = self._module_of(func_name)
            modules.setdefault(module, []).append((func_name, fi))
        
        for module, funcs in sorted(modules.items()):
            safe_module = self._safe_module(module)
            lines.append(f"    subgraph {safe_module}")
            for func_name, fi in funcs:
                sid = self._readable_id(func_name)
                short = fi.name[:35]
                cc = self._get_cc(fi)
                if cc >= 15:
                    lines.append(f'        {sid}{{{{{short} CC={cc}}}}}')
                elif cc >= 8:
                    lines.append(f'        {sid}("{short} CC={cc}")')
                else:
                    lines.append(f'        {sid}["{short}"]')
            lines.append("    end")
            lines.append("")
        
        # Edges — all cross-function calls
        seen_edges: Set[Tuple[str, str]] = set()
        for func_name, fi in filtered_funcs.items():
            src = self._readable_id(func_name)
            for callee in fi.calls[:15]:
                resolved = self._resolve(callee, filtered_funcs)
                if resolved and resolved != func_name:
                    dst = self._readable_id(resolved)
                    edge = (src, dst)
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        lines.append(f"    {src} --> {dst}")
        
        # CC-based styling
        high_nodes = []
        med_nodes = []
        for func_name, fi in filtered_funcs.items():
            cc = self._get_cc(fi)
            sid = self._readable_id(func_name)
            if cc >= 15:
                high_nodes.append(sid)
            elif cc >= 8:
                med_nodes.append(sid)
        
        if high_nodes:
            lines.append(f"    class {','.join(high_nodes[:50])} highCC")
        if med_nodes:
            lines.append(f"    class {','.join(med_nodes[:50])} medCC")
        if entry_points:
            entry_ids = [self._readable_id(ep) for ep in entry_points[:15]]
            lines.append(f"    class {','.join(entry_ids)} entry")
        
        self._write(output_path, lines)

    def _readable_id(self, name: str) -> str:
        """Create human-readable Mermaid-safe unique node ID.
        
        Pattern: module__ClassName__method (ensures uniqueness across modules)
        Examples:
          code2llm.core.analyze → code2llm__core__analyze
          code2llm.core.PipelineDetector.__init__ → code2llm__core__PipelineDetector____init__
        """
        # Convert dots to double underscores to preserve hierarchy
        safe = name.replace('.', '__')
        # Replace other unsafe chars
        safe = safe.replace('-', '_').replace(':', '_').replace(' ', '_')
        # Keep reasonable length but preserve class+method uniqueness
        if len(safe) > 60:
            parts = name.split('.')
            if len(parts) >= 3:
                # module__Class__method or module__subpackage__Class__method
                module = parts[0]
                method = parts[-1]
                # Include class name if present (parts[-2] is usually class or subpackage)
                if len(parts) >= 4 and parts[-2][0].isupper():
                    # Definitely a class: module.sub.Class.method
                    class_name = parts[-2]
                    safe = f"{module}__{class_name}__{method}"
                else:
                    # Might be module.subpackage.function
                    middle = '__'.join(parts[1:-1])
                    safe = f"{module}__{middle}__{method}"
            safe = safe[:60]
        return safe

    def _safe_module(self, name: str) -> str:
        """Create safe subgraph name."""
        return name.replace('.', '_').replace('-', '_').replace('/', '_').replace(' ', '_')

    def _module_of(self, func_name: str) -> str:
        """Extract module from qualified name.

        Returns up to 2 levels (e.g. 'code2llm.core', 'code2llm.exporters')
        so that subpackage-level cross-edges are visible in compact_flow.
        """
        parts = func_name.split('.')
        if len(parts) >= 3:
            return '.'.join(parts[:2])
        if len(parts) == 2:
            return parts[0]
        return parts[0] if parts else 'unknown'

    def _resolve(self, callee: str, funcs: dict) -> str:
        """Resolve callee to a known qualified name."""
        if callee in funcs:
            return callee
        candidates = [qn for qn in funcs if qn.endswith(f".{callee}")]
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _write(self, path: str, lines: list) -> None:
        """Write lines to file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
