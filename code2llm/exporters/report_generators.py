"""Report generators — produce views from project.yaml (single source of truth).

Generators:
  ToonViewGenerator     → project.toon  (compact human-scannable)
  ContextViewGenerator  → context.md    (deduplicated LLM narrative)
  ArticleViewGenerator  → status.md     (publishable status article)
  HTMLDashboardGenerator → dashboard.html (web visualization)
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_project_yaml(path: str) -> Dict[str, Any]:
    """Load and validate project.yaml."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "version" not in data:
        raise ValueError(f"Invalid project.yaml: missing 'version' key in {path}")
    return data


# ======================================================================
# TOON VIEW — compact ~50 lines for quick human scanning
# ======================================================================
class ToonViewGenerator:
    """Generate project.toon from project.yaml data."""

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        lines = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _render(self, data: Dict[str, Any]) -> List[str]:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])

        lines: List[str] = []

        # Header
        stats = proj.get("stats", {})
        lines.append(
            f"# {proj.get('name', '?')} | "
            f"{stats.get('functions', 0)} func | "
            f"{stats.get('files', 0)}f | "
            f"{stats.get('lines', 0)}L | "
            f"{proj.get('analyzed_at', '?')[:10]}"
        )
        lines.append("")

        # Health summary
        lines.append("HEALTH:")
        lines.append(
            f"  CC̄={health.get('cc_avg', 0)}  "
            f"critical={health.get('critical_count', 0)} (limit:{health.get('critical_limit', 10)})  "
            f"dup={health.get('duplicates', 0)}  "
            f"cycles={health.get('cycles', 0)}"
        )

        # Alerts
        alerts = health.get("alerts", [])
        if alerts:
            lines.append("")
            lines.append(f"ALERTS[{len(alerts)}]:")
            for a in alerts[:10]:
                sev = "!!" if a.get("severity") == "critical" else "!"
                lines.append(
                    f"  {sev:2s} {a.get('type', '?'):16s} "
                    f"{a.get('target', '?')} = {a.get('value', '?')} "
                    f"(limit:{a.get('limit', '?')})"
                )

        # Top modules by CC
        lines.append("")
        top_mods = [m for m in modules if m.get("cc_max", 0) > 0][:10]
        lines.append(f"MODULES[{len(modules)}] (top by CC):")
        for m in top_mods:
            lines.append(
                f"  M[{m.get('path', '?')}] "
                f"{m.get('lines', 0)}L "
                f"C:{m.get('classes', 0)} "
                f"M:{m.get('methods', 0)} "
                f"CC↑{m.get('cc_max', 0)} "
                f"D:{m.get('inbound_deps', 0)}"
            )

        # Hotspots
        if hotspots:
            lines.append("")
            lines.append(f"HOTSPOTS[{len(hotspots)}]:")
            for h in hotspots[:5]:
                lines.append(
                    f"  ★ {h.get('name', '?')} fan={h.get('fan_out', 0)}  "
                    f"// {h.get('note', '')}"
                )

        # Refactoring
        priorities = refactoring.get("priorities", [])
        if priorities:
            lines.append("")
            lines.append(f"REFACTOR[{len(priorities)}]:")
            for i, p in enumerate(priorities[:5], 1):
                impact = p.get("impact", "?")[0].upper()
                effort = p.get("effort", "?")[0].upper()
                lines.append(f"  [{i}] {impact}/{effort} {p.get('action', '?')}")

        # Evolution (last 3 entries)
        if evolution:
            lines.append("")
            lines.append("EVOLUTION:")
            for e in evolution[-3:]:
                lines.append(
                    f"  {e.get('date', '?')} CC̄={e.get('cc_avg', '?')} "
                    f"crit={e.get('critical', '?')} "
                    f"{e.get('lines', '?')}L "
                    f"// {e.get('note', '')}"
                )

        return lines


# ======================================================================
# CONTEXT VIEW — deduplicated LLM narrative (~150 lines)
# ======================================================================
class ContextViewGenerator:
    """Generate context.md from project.yaml data."""

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        lines = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _render(self, data: Dict[str, Any]) -> List[str]:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})

        lines: List[str] = []

        # Header
        lines.append("# System Architecture Analysis")
        lines.append("")

        # Overview
        stats = proj.get("stats", {})
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Project**: {proj.get('name', '?')}")
        lines.append(f"- **Language**: {proj.get('language', '?')}")
        lines.append(f"- **Files**: {stats.get('files', 0)}")
        lines.append(f"- **Lines**: {stats.get('lines', 0)}")
        lines.append(f"- **Functions**: {stats.get('functions', 0)}")
        lines.append(f"- **Classes**: {stats.get('classes', 0)}")
        lines.append(f"- **Avg CC**: {health.get('cc_avg', 0)}")
        lines.append(f"- **Critical (CC≥{health.get('critical_limit', 10)})**: {health.get('critical_count', 0)}")
        lines.append("")

        # Architecture — modules grouped by directory
        lines.append("## Architecture")
        lines.append("")
        dir_groups: Dict[str, List[Dict]] = {}
        for m in modules:
            path = m.get("path", "")
            parts = Path(path).parts
            dir_key = str(Path(*parts[:-1])) if len(parts) > 1 else "root"
            if dir_key not in dir_groups:
                dir_groups[dir_key] = []
            dir_groups[dir_key].append(m)

        for dir_name in sorted(dir_groups.keys()):
            group = dir_groups[dir_name]
            total_lines = sum(m.get("lines", 0) for m in group)
            total_funcs = sum(m.get("methods", 0) for m in group)
            lines.append(f"### {dir_name}/ ({len(group)} files, {total_lines}L, {total_funcs} functions)")
            lines.append("")
            for m in sorted(group, key=lambda x: x.get("cc_max", 0), reverse=True)[:5]:
                fname = Path(m.get("path", "")).name
                lines.append(
                    f"- `{fname}` — {m.get('lines', 0)}L, "
                    f"{m.get('methods', 0)} methods, "
                    f"CC↑{m.get('cc_max', 0)}"
                )
            if len(group) > 5:
                lines.append(f"- _{len(group) - 5} more files_")
            lines.append("")

        # Key exports (classes and functions with high CC)
        lines.append("## Key Exports")
        lines.append("")
        for m in modules:
            for exp in m.get("exports", []):
                if exp.get("type") == "class":
                    methods = exp.get("methods", [])
                    flagged = [me for me in methods if me.get("flag")]
                    if flagged or exp.get("cc_avg", 0) >= 5:
                        lines.append(f"- **{exp['name']}** (class, CC̄={exp.get('cc_avg', 0)})")
                        for me in flagged:
                            lines.append(f"  - `{me['name']}` CC={me.get('cc', 0)} ⚠ {me.get('flag', '')}")
                elif exp.get("type") == "function" and exp.get("flag"):
                    lines.append(f"- **{exp['name']}** (function, CC={exp.get('cc', 0)}) ⚠ {exp.get('flag', '')}")
        lines.append("")

        # Hotspots
        if hotspots:
            lines.append("## Hotspots (High Fan-Out)")
            lines.append("")
            for h in hotspots[:7]:
                lines.append(f"- **{h['name']}** — fan-out={h['fan_out']}: {h.get('note', '')}")
            lines.append("")

        # Refactoring priorities
        priorities = refactoring.get("priorities", [])
        if priorities:
            lines.append("## Refactoring Priorities")
            lines.append("")
            lines.append("| # | Action | Impact | Effort |")
            lines.append("|---|--------|--------|--------|")
            for i, p in enumerate(priorities[:10], 1):
                lines.append(
                    f"| {i} | {p.get('action', '?')} | {p.get('impact', '?')} | {p.get('effort', '?')} |"
                )
            lines.append("")

        # Guidelines
        lines.append("## Context for LLM")
        lines.append("")
        lines.append("When suggesting changes:")
        lines.append("1. Start from hotspots and high-CC functions")
        lines.append("2. Follow refactoring priorities above")
        lines.append("3. Maintain public API surface — keep backward compatibility")
        lines.append("4. Prefer minimal, incremental changes")
        lines.append("")

        return lines


# ======================================================================
# ARTICLE VIEW — publishable status article (status.md)
# ======================================================================
class ArticleViewGenerator:
    """Generate status.md — publishable project health article."""

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        lines = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _render(self, data: Dict[str, Any]) -> List[str]:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])
        stats = proj.get("stats", {})

        lines: List[str] = []

        # Front matter
        lines.append("---")
        lines.append(f"title: \"Project Health Report: {proj.get('name', '?')}\"")
        lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"tool: code2llm")
        lines.append("---")
        lines.append("")

        # Title
        lines.append(f"# Project Health Report: {proj.get('name', '?')}")
        lines.append("")
        lines.append(
            f"Automated analysis of **{proj.get('name', '?')}** "
            f"({stats.get('files', 0)} files, {stats.get('lines', 0)} lines) "
            f"generated on {proj.get('analyzed_at', '?')[:10]}."
        )
        lines.append("")

        # Health summary
        lines.append("## Health Summary")
        lines.append("")
        cc_avg = health.get("cc_avg", 0)
        crit = health.get("critical_count", 0)
        if cc_avg <= 5 and crit <= 5:
            emoji = "🟢"
            verdict = "Good"
        elif cc_avg <= 8 and crit <= 15:
            emoji = "🟡"
            verdict = "Needs attention"
        else:
            emoji = "🔴"
            verdict = "Critical"

        lines.append(f"**Overall: {emoji} {verdict}**")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Average CC | {cc_avg} |")
        lines.append(f"| Critical functions (CC≥{health.get('critical_limit', 10)}) | {crit} |")
        lines.append(f"| Duplicates | {health.get('duplicates', 0)} |")
        lines.append(f"| Circular dependencies | {health.get('cycles', 0)} |")
        lines.append(f"| Total functions | {stats.get('functions', 0)} |")
        lines.append(f"| Total classes | {stats.get('classes', 0)} |")
        lines.append("")

        # Alerts
        alerts = health.get("alerts", [])
        if alerts:
            lines.append("## Alerts")
            lines.append("")
            for a in alerts[:10]:
                sev_icon = "🔴" if a.get("severity") == "critical" else "🟡"
                lines.append(
                    f"- {sev_icon} **{a.get('target', '?')}**: "
                    f"{a.get('type', '?')} = {a.get('value', '?')} "
                    f"(limit: {a.get('limit', '?')})"
                )
            lines.append("")

        # Top hotspots
        if hotspots:
            lines.append("## Hotspots")
            lines.append("")
            lines.append("Functions with highest fan-out (orchestration complexity):")
            lines.append("")
            for h in hotspots[:5]:
                lines.append(f"- **{h['name']}** (fan-out: {h['fan_out']}) — {h.get('note', '')}")
            lines.append("")

        # Refactoring roadmap
        priorities = refactoring.get("priorities", [])
        if priorities:
            lines.append("## Refactoring Roadmap")
            lines.append("")
            for i, p in enumerate(priorities[:7], 1):
                impact_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(p.get("impact"), "⚪")
                lines.append(f"{i}. {impact_icon} **{p.get('action', '?')}** (effort: {p.get('effort', '?')})")
            lines.append("")

        # Evolution trend
        if len(evolution) > 1:
            lines.append("## Evolution")
            lines.append("")
            lines.append("| Date | CC̄ | Critical | Lines | Note |")
            lines.append("|------|-----|----------|-------|------|")
            for e in evolution[-10:]:
                lines.append(
                    f"| {e.get('date', '?')} | {e.get('cc_avg', '?')} | "
                    f"{e.get('critical', '?')} | {e.get('lines', '?')} | "
                    f"{e.get('note', '')} |"
                )
            lines.append("")

            # Trend
            first = evolution[0]
            last = evolution[-1]
            cc_delta = (last.get("cc_avg", 0) or 0) - (first.get("cc_avg", 0) or 0)
            if cc_delta < 0:
                lines.append(f"📈 **CC improved** by {abs(cc_delta):.1f} since {first.get('date', '?')}")
            elif cc_delta > 0:
                lines.append(f"📉 **CC worsened** by {cc_delta:.1f} since {first.get('date', '?')}")
            else:
                lines.append(f"➡️ **CC stable** since {first.get('date', '?')}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Generated by code2llm on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")

        return lines


# ======================================================================
# HTML DASHBOARD — web visualization with trend charts
# ======================================================================
class HTMLDashboardGenerator:
    """Generate dashboard.html from project.yaml data."""

    def generate(self, data: Dict[str, Any], output_path: str) -> None:
        html = self._render(data)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _render(self, data: Dict[str, Any]) -> str:
        proj = data.get("project", {})
        health = data.get("health", {})
        modules = data.get("modules", [])
        hotspots = data.get("hotspots", [])
        refactoring = data.get("refactoring", {})
        evolution = data.get("evolution", [])
        stats = proj.get("stats", {})

        # Evolution data for chart
        evo_dates = [e.get("date", "") for e in evolution]
        evo_cc = [e.get("cc_avg", 0) for e in evolution]
        evo_crit = [e.get("critical", 0) for e in evolution]

        # Module CC data for bar chart
        top_modules = sorted(modules, key=lambda m: m.get("cc_max", 0), reverse=True)[:15]
        mod_names = [Path(m.get("path", "")).name for m in top_modules]
        mod_cc = [m.get("cc_max", 0) for m in top_modules]

        cc_avg = health.get("cc_avg", 0)
        if cc_avg <= 5:
            health_color = "#22c55e"
            health_label = "Good"
        elif cc_avg <= 8:
            health_color = "#eab308"
            health_label = "Warning"
        else:
            health_color = "#ef4444"
            health_label = "Critical"

        alerts_html = ""
        for a in health.get("alerts", [])[:15]:
            sev_class = "critical" if a.get("severity") == "critical" else "warning"
            alerts_html += f"""
            <tr class="{sev_class}">
                <td><span class="badge {sev_class}">{a.get('severity', '?')}</span></td>
                <td>{a.get('target', '?')}</td>
                <td>{a.get('type', '?')}</td>
                <td>{a.get('value', '?')}</td>
                <td>{a.get('limit', '?')}</td>
            </tr>"""

        hotspots_html = ""
        for h in hotspots[:10]:
            hotspots_html += f"""
            <tr>
                <td><strong>{h.get('name', '?')}</strong></td>
                <td>{h.get('fan_out', 0)}</td>
                <td>{h.get('note', '')}</td>
            </tr>"""

        refactor_html = ""
        for i, p in enumerate(refactoring.get("priorities", [])[:10], 1):
            impact_class = p.get("impact", "low")
            refactor_html += f"""
            <tr>
                <td>{i}</td>
                <td>{p.get('action', '?')}</td>
                <td><span class="badge {impact_class}">{p.get('impact', '?')}</span></td>
                <td>{p.get('effort', '?')}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{proj.get('name', 'Project')} — Health Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8;
    --green: #22c55e; --yellow: #eab308; --red: #ef4444; --blue: #3b82f6;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:2rem; }}
  h1 {{ font-size:1.5rem; margin-bottom:.5rem; }}
  h2 {{ font-size:1.1rem; color:var(--muted); margin:1.5rem 0 .75rem; border-bottom:1px solid var(--border); padding-bottom:.25rem; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; margin:1rem 0; }}
  .card {{ background:var(--surface); border:1px solid var(--border); border-radius:.5rem; padding:1rem; }}
  .card .value {{ font-size:1.8rem; font-weight:700; }}
  .card .label {{ color:var(--muted); font-size:.8rem; text-transform:uppercase; }}
  .chart-container {{ background:var(--surface); border:1px solid var(--border); border-radius:.5rem; padding:1rem; margin:1rem 0; }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  th {{ text-align:left; color:var(--muted); padding:.5rem; border-bottom:1px solid var(--border); }}
  td {{ padding:.5rem; border-bottom:1px solid var(--border); }}
  .badge {{ padding:.15rem .5rem; border-radius:.25rem; font-size:.75rem; font-weight:600; }}
  .badge.critical {{ background:var(--red); color:#fff; }}
  .badge.warning {{ background:var(--yellow); color:#000; }}
  .badge.high {{ background:var(--red); color:#fff; }}
  .badge.medium {{ background:var(--yellow); color:#000; }}
  .badge.low {{ background:var(--green); color:#fff; }}
  tr.critical td {{ background:rgba(239,68,68,.08); }}
  tr.warning td {{ background:rgba(234,179,8,.05); }}
  .health-indicator {{ display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:.5rem; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
  @media (max-width:768px) {{ .two-col {{ grid-template-columns:1fr; }} }}
  footer {{ margin-top:2rem; color:var(--muted); font-size:.75rem; text-align:center; }}
</style>
</head>
<body>
<h1>
  <span class="health-indicator" style="background:{health_color}"></span>
  {proj.get('name', 'Project')} — {health_label}
</h1>
<p style="color:var(--muted);font-size:.85rem;">
  Analyzed {proj.get('analyzed_at', '?')[:10]} by code2llm
</p>

<div class="grid">
  <div class="card"><div class="value">{cc_avg}</div><div class="label">Avg CC</div></div>
  <div class="card"><div class="value">{health.get('critical_count', 0)}</div><div class="label">Critical (CC≥{health.get('critical_limit', 10)})</div></div>
  <div class="card"><div class="value">{stats.get('functions', 0)}</div><div class="label">Functions</div></div>
  <div class="card"><div class="value">{stats.get('classes', 0)}</div><div class="label">Classes</div></div>
  <div class="card"><div class="value">{stats.get('files', 0)}</div><div class="label">Files</div></div>
  <div class="card"><div class="value">{stats.get('lines', 0)}</div><div class="label">Lines</div></div>
  <div class="card"><div class="value">{health.get('duplicates', 0)}</div><div class="label">Duplicates</div></div>
  <div class="card"><div class="value">{health.get('cycles', 0)}</div><div class="label">Cycles</div></div>
</div>

<div class="two-col">
  <div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Evolution</h2>
    <canvas id="evoChart" height="200"></canvas>
  </div>
  <div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Module CC (top 15)</h2>
    <canvas id="modChart" height="200"></canvas>
  </div>
</div>

<h2>Alerts ({len(health.get('alerts', []))})</h2>
<div class="card">
<table>
  <thead><tr><th>Severity</th><th>Target</th><th>Type</th><th>Value</th><th>Limit</th></tr></thead>
  <tbody>{alerts_html if alerts_html else '<tr><td colspan="5" style="color:var(--muted)">No alerts</td></tr>'}</tbody>
</table>
</div>

<div class="two-col">
<div>
<h2>Hotspots ({len(hotspots)})</h2>
<div class="card">
<table>
  <thead><tr><th>Function</th><th>Fan-out</th><th>Note</th></tr></thead>
  <tbody>{hotspots_html if hotspots_html else '<tr><td colspan="3" style="color:var(--muted)">No hotspots</td></tr>'}</tbody>
</table>
</div>
</div>

<div>
<h2>Refactoring Priorities ({len(refactoring.get('priorities', []))})</h2>
<div class="card">
<table>
  <thead><tr><th>#</th><th>Action</th><th>Impact</th><th>Effort</th></tr></thead>
  <tbody>{refactor_html if refactor_html else '<tr><td colspan="4" style="color:var(--muted)">No refactoring needed</td></tr>'}</tbody>
</table>
</div>
</div>
</div>

<footer>Generated by code2llm on {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>

<script>
const evoCtx = document.getElementById('evoChart').getContext('2d');
new Chart(evoCtx, {{
  type: 'line',
  data: {{
    labels: {evo_dates},
    datasets: [
      {{ label: 'CC avg', data: {evo_cc}, borderColor: '#3b82f6', tension: .3, yAxisID: 'y' }},
      {{ label: 'Critical', data: {evo_crit}, borderColor: '#ef4444', tension: .3, yAxisID: 'y1' }}
    ]
  }},
  options: {{
    responsive: true,
    scales: {{
      y: {{ position:'left', grid:{{color:'#334155'}}, ticks:{{color:'#94a3b8'}} }},
      y1: {{ position:'right', grid:{{drawOnChartArea:false}}, ticks:{{color:'#94a3b8'}} }},
      x: {{ ticks:{{color:'#94a3b8'}}, grid:{{color:'#334155'}} }}
    }},
    plugins: {{ legend: {{ labels: {{ color:'#e2e8f0' }} }} }}
  }}
}});

const modCtx = document.getElementById('modChart').getContext('2d');
new Chart(modCtx, {{
  type: 'bar',
  data: {{
    labels: {mod_names},
    datasets: [{{ label: 'Max CC', data: {mod_cc},
      backgroundColor: {mod_cc}.map(v => v >= 15 ? '#ef4444' : v >= 10 ? '#eab308' : '#22c55e')
    }}]
  }},
  options: {{
    responsive: true, indexAxis: 'y',
    scales: {{
      x: {{ grid:{{color:'#334155'}}, ticks:{{color:'#94a3b8'}} }},
      y: {{ grid:{{color:'#334155'}}, ticks:{{color:'#94a3b8',font:{{size:10}}}} }}
    }},
    plugins: {{ legend: {{ display:false }} }}
  }}
}});
</script>
</body>
</html>"""
