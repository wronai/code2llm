"""Context Exporter for code2flow — generates context.md (LLM narrative).

Rename from llm_exporter.py → context_exporter.py (Sprint 4, v0.3.3).
Produces LLM-ready architecture summary with flows, patterns, and API surface.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from .base import Exporter
from ..core.models import AnalysisResult, FunctionInfo


class ContextExporter(Exporter):
    """Export LLM-ready analysis summary with architecture and flows.

    Output: context.md — architecture narrative for LLM consumption.
    Formerly LLMPromptExporter in llm_exporter.py.
    """
    
    def export(self, result: AnalysisResult, output_path: str) -> None:
        """Generate comprehensive LLM prompt with architecture description."""
        lines = ["# System Architecture Analysis", ""]
        
        # Collect sections
        lines.extend(self._get_overview(result))
        lines.extend(self._get_architecture_by_module(result))
        
        important_entries = self._get_important_entries(result)
        lines.extend(self._get_key_entry_points(important_entries))
        lines.extend(self._get_process_flows(result, important_entries))
        
        lines.extend(self._get_key_classes(result))
        lines.extend(self._get_data_transformations(result))
        lines.extend(self._get_behavioral_patterns(result))
        lines.extend(self._get_api_surface(result))
        lines.extend(self._get_system_interactions(important_entries))
        
        lines.extend([
            "## Reverse Engineering Guidelines",
            "",
            "1. **Entry Points**: Start analysis from the entry points listed above",
            "2. **Core Logic**: Focus on classes with many methods",
            "3. **Data Flow**: Follow data transformation functions",
            "4. **Process Flows**: Use the flow diagrams for execution paths",
            "5. **API Surface**: Public API functions reveal the interface",
            "",
            "## Context for LLM",
            "",
            "Maintain the identified architectural patterns and public API surface when suggesting changes.",
        ])
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _get_overview(self, result: AnalysisResult) -> List[str]:
        return [
            "## Overview",
            "",
            f"- **Project**: {result.project_path}",
            f"- **Analysis Mode**: {result.analysis_mode}",
            f"- **Total Functions**: {len(result.functions)}",
            f"- **Total Classes**: {len(result.classes)}",
            f"- **Modules**: {len(result.modules)}",
            f"- **Entry Points**: {len(result.entry_points)}",
            "",
        ]

    def _get_architecture_by_module(self, result: AnalysisResult) -> List[str]:
        lines = ["## Architecture by Module", ""]
        module_stats = []
        for mod_name, mod in result.modules.items():
            if len(mod.functions) > 0 or len(mod.classes) > 0:
                module_stats.append((mod_name, len(mod.functions), len(mod.classes), mod.file))
        
        module_stats.sort(key=lambda x: x[1], reverse=True)
        for mod_name, f_count, c_count, file_path in module_stats[:20]:
            lines.append(f"### {mod_name}")
            lines.append(f"- **Functions**: {f_count}")
            if c_count > 0: lines.append(f"- **Classes**: {c_count}")
            if file_path: lines.append(f"- **File**: `{Path(file_path).name}`")
            lines.append("")
        return lines

    def _get_important_entries(self, result: AnalysisResult) -> List[Tuple[str, int, Any]]:
        entries = []
        for ep in result.entry_points:
            func = result.functions.get(ep)
            if func:
                score = len(func.calls) + len(func.called_by)
                entries.append((ep, score, func))
        entries.sort(key=lambda x: x[1], reverse=True)
        return entries

    def _get_key_entry_points(self, important_entries: List[Tuple[str, int, Any]]) -> List[str]:
        lines = ["## Key Entry Points", "", "Main execution flows into the system:", ""]
        for ep, _, func in important_entries[:30]:
            lines.append(f"### {ep}")
            if func.docstring: lines.append(f"> {func.docstring[:150]}")
            if func.calls: lines.append(f"- **Calls**: {', '.join(func.calls[:8])}")
            lines.append("")
        return lines

    def _get_process_flows(self, result: AnalysisResult, important_entries: List[Tuple[str, int, Any]]) -> List[str]:
        lines = ["## Process Flows", "", "Key execution flows identified:", ""]
        flow_id, seen_flows, seen_base_names = 1, set(), set()
        for ep_name, _, ep_func in important_entries[:20]:
            base_name = ep_name.split('.')[-1]
            if base_name in seen_base_names: continue
            seen_base_names.add(base_name)
            flow = self._trace_flow(ep_name, ep_func, result, depth=3)
            if flow and flow not in seen_flows:
                seen_flows.add(flow)
                lines.extend([f"### Flow {flow_id}: {base_name}", "```", flow, "```", ""])
                flow_id += 1
                if flow_id > 10: break
        return lines

    def _get_key_classes(self, result: AnalysisResult) -> List[str]:
        if not result.classes: return []
        lines = ["## Key Classes", ""]
        class_list = sorted(result.classes.items(), key=lambda x: len(x[1].methods), reverse=True)
        for cls_name, cls in class_list[:20]:
            lines.append(f"### {cls_name}")
            if cls.docstring: lines.append(f"> {cls.docstring[:100]}")
            lines.append(f"- **Methods**: {len(cls.methods)}")
            if cls.methods: lines.append(f"- **Key Methods**: {', '.join(cls.methods[:10])}")
            if cls.bases: lines.append(f"- **Inherits**: {', '.join(cls.bases)}")
            lines.append("")
        return lines

    def _get_data_transformations(self, result: AnalysisResult) -> List[str]:
        lines = ["## Data Transformation Functions", "", "Key functions that process and transform data:", ""]
        data_indicators = ['parse', 'transform', 'convert', 'process', 'validate', 'serialize', 'deserialize', 'encode', 'decode', 'format']
        data_funcs = [
            (name, f) for name, f in result.functions.items() 
            if any(ind in f.name.lower() for ind in data_indicators)
        ]
        for func_name, func in data_funcs[:25]:
            lines.append(f"### {func_name}")
            if func.docstring: lines.append(f"> {func.docstring[:100]}")
            if func.calls: lines.append(f"- **Output to**: {', '.join(func.calls[:5])}")
            lines.append("")
        return lines

    def _get_behavioral_patterns(self, result: AnalysisResult) -> List[str]:
        if not result.patterns: return []
        lines = ["## Behavioral Patterns", ""]
        for pattern in result.patterns[:15]:
            lines.append(f"### {pattern.name}")
            lines.append(f"- **Type**: {pattern.type}")
            lines.append(f"- **Confidence**: {pattern.confidence:.2f}")
            if pattern.functions: lines.append(f"- **Functions**: {', '.join(pattern.functions[:5])}")
            lines.append("")
        return lines

    def _get_api_surface(self, result: AnalysisResult) -> List[str]:
        lines = ["## Public API Surface", "", "Functions exposed as public API (no underscore prefix):", ""]
        public_funcs = sorted(
            [(n, f) for n, f in result.functions.items() if not f.name.startswith('_') and '.' in n],
            key=lambda x: len(x[1].calls), reverse=True
        )
        for func_name, func in public_funcs[:40]:
            lines.append(f"- `{func_name}` - {len(func.calls)} calls")
        lines.append("")
        return lines

    def _get_system_interactions(self, important_entries: List[Tuple[str, int, Any]]) -> List[str]:
        lines = ["## System Interactions", "", "How components interact:", "", "```mermaid", "graph TD"]
        added_edges = set()
        for ep_name, _, ep_func in important_entries[:15]:
            for called in ep_func.calls[:5]:
                edge = (ep_name.split('.')[-1][:20], called.split('.')[-1][:20])
                if edge not in added_edges and len(added_edges) < 30:
                    added_edges.add(edge)
                    lines.append(f"    {edge[0]} --> {edge[1]}")
        lines.extend(["```", ""])
        return lines

    def _trace_flow(self, func_name: str, func, result: AnalysisResult, depth: int, visited: set = None) -> str:
        """Trace execution flow from a function with cycle detection."""
        if visited is None: visited = set()
        if func_name in visited or depth <= 0: return func_name.split('.')[-1]
        
        visited.add(func_name)
        short_name = func_name.split('.')[-1]
        module = func_name.rsplit('.', 1)[0] if '.' in func_name else 'root'
        lines = [f"{short_name} [{module}]"]
        
        calls_by_module = {}
        for called in func.calls[:5]:
            mod = called.rsplit('.', 1)[0] if '.' in called else 'root'
            if mod not in calls_by_module: calls_by_module[mod] = []
            calls_by_module[mod].append(called)
        
        shown = 0
        for mod, calls in sorted(calls_by_module.items(), key=lambda x: x[0] != module):
            for called in calls[:2]:
                if shown >= 3: break
                called_func = result.functions.get(called)
                if called_func and called not in visited:
                    sub_flow = self._trace_flow(called, called_func, result, depth - 1, visited.copy())
                    cross = " →" if mod != module else ""
                    lines.append(f"  └─{cross}> {called.split('.')[-1]}")
                    for sub in sub_flow.split('\n')[1:][:3]: lines.append("    " + sub)
                    shown += 1
        return '\n'.join(lines)
