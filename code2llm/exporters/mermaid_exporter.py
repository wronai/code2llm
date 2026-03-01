"""Mermaid Exporter for code2llm.

Three distinct outputs:
  - export()           → flow.mmd   — full call graph with CC-based styling
  - export_call_graph() → calls.mmd  — simplified call graph (edges only, no isolates)
  - export_compact()    → compact_flow.mmd — module-level aggregation
"""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .base import Exporter
from ..core.models import AnalysisResult


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
    # Helpers
    # ------------------------------------------------------------------ #
    def _readable_id(self, name: str) -> str:
        """Create human-readable Mermaid-safe node ID."""
        # module.Class.method → module__Class_method
        safe = name.replace('.', '__').replace('-', '_').replace(':', '_')
        safe = safe.replace(' ', '_')
        if len(safe) > 50:
            # Keep module prefix + function name
            parts = name.split('.')
            if len(parts) >= 2:
                safe = f"{parts[0]}__{parts[-1]}"
            safe = safe[:50]
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
