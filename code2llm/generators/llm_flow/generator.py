"""LLM Flow generator — main flow generation and rendering."""

from typing import Any, Dict, List

from .utils import _as_dict, _as_list, _shorten
from .nodes import _collect_nodes, _collect_entrypoints, _collect_functions
from .analysis import (
    _summarize_functions,
    _pick_relevant_functions,
)


def generate_llm_flow(
    analysis: Dict[str, Any],
    max_functions: int,
    limit_decisions: int,
    limit_calls: int,
) -> Dict[str, Any]:
    nodes = _collect_nodes(analysis)
    entrypoints = _collect_entrypoints(nodes)

    known_functions = _collect_functions(nodes)
    func_summaries = _summarize_functions(nodes, limit_decisions=limit_decisions, limit_calls=limit_calls)

    reachable = _pick_relevant_functions(
        entrypoints=entrypoints,
        known_functions=known_functions,
        func_summaries=func_summaries,
        nodes=nodes,
        max_functions=max_functions,
    )

    functions_out: List[Dict[str, Any]] = []
    for fn in sorted(reachable):
        s = func_summaries.get(fn)
        if not s:
            continue
        functions_out.append(
            {
                "name": s.name,
                "file": s.file,
                "line": s.line,
                "decisions": list(s.decisions),
                "calls": list(s.calls),
            }
        )

    package_names = sorted({fn.split(".")[0] for fn in known_functions if "." in fn})

    return {
        "format": "llm_flow.v1",
        "app": {
            "packages": package_names,
            "entrypoints": entrypoints,
        },
        "flow": {
            "selected_functions": functions_out,
        },
    }


def render_llm_flow_md(flow: Dict[str, Any]) -> str:
    app = _as_dict(flow.get("app"))
    entrypoints = _as_list(app.get("entrypoints"))
    selected = _as_list(_as_dict(flow.get("flow")).get("selected_functions"))

    lines: List[str] = []
    lines.append("# LLM Flow Summary")
    lines.append("")

    pkgs = _as_list(app.get("packages"))
    if pkgs:
        lines.append("## Packages")
        for p in pkgs:
            lines.append(f"- {p}")
        lines.append("")

    if entrypoints:
        lines.append("## Entrypoints")
        for ep in entrypoints:
            epd = _as_dict(ep)
            fn = epd.get("function")
            f = epd.get("file")
            ln = epd.get("line")
            lines.append(f"- {fn} ({f}:{ln})")
        lines.append("")

    lines.append("## Selected functions")
    for f in selected:
        fd = _as_dict(f)
        name = fd.get("name")
        file = fd.get("file")
        line = fd.get("line")
        lines.append(f"### {name}")
        lines.append(f"- Location: {file}:{line}")

        decisions = _as_list(fd.get("decisions"))
        if decisions:
            lines.append("- Decisions:")
            for d in decisions:
                lines.append(f"  - {_shorten(str(d), 180)}")

        calls = _as_list(fd.get("calls"))
        if calls:
            lines.append("- Calls:")
            for c in calls:
                lines.append(f"  - {c}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    'generate_llm_flow',
    'render_llm_flow_md',
]
