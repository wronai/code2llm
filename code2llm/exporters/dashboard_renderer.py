"""Dashboard HTML Renderer — generates dashboard.html with charts.

Renders the complete HTML dashboard with embedded Chart.js visualizations.
"""

from datetime import datetime
from typing import Any, Dict


class DashboardRenderer:
    """Render HTML dashboard from prepared data structures."""

    def render(
        self,
        proj: Dict[str, Any],
        stats: Dict[str, Any],
        health: Dict[str, Any],
        cc_avg: float,
        health_color: str,
        health_label: str,
        evo_chart: Dict[str, Any],
        lang_data: Dict[str, Any],
        mod_lines_chart: Dict[str, Any],
        mod_funcs_chart: Dict[str, Any],
        alerts_html: str,
        hotspots_html: str,
        refactor_html: str,
        top_modules_html: str,
        modules: list,
        hotspots: list,
        refactoring: Dict[str, Any],
    ) -> str:
        """Render complete dashboard HTML."""
        evo_section = self._render_evolution_section(evo_chart)
        evo_script = self._render_evolution_script(evo_chart)
        lang_summary = ', '.join(f'{n}: {c}' for n, c in zip(lang_data['names'], lang_data['files']))

        return self._assemble_html(
            proj=proj, stats=stats, health=health,
            cc_avg=cc_avg, health_color=health_color, health_label=health_label,
            evo_section=evo_section, evo_script=evo_script, lang_data=lang_data,
            lang_summary=lang_summary, mod_lines_chart=mod_lines_chart,
            mod_funcs_chart=mod_funcs_chart, alerts_html=alerts_html,
            hotspots_html=hotspots_html, refactor_html=refactor_html,
            top_modules_html=top_modules_html, modules=modules,
            hotspots=hotspots, refactoring=refactoring,
        )

    def _assemble_html(self, **ctx) -> str:
        """Assemble the complete HTML document with all charts and tables."""
        proj = ctx["proj"]
        stats = ctx["stats"]
        health = ctx["health"]
        cc_avg = ctx["cc_avg"]
        health_color = ctx["health_color"]
        health_label = ctx["health_label"]
        evo = ctx["evo_section"]
        evo_script = ctx["evo_script"]
        lang = ctx["lang_data"]
        lang_summary = ctx["lang_summary"]
        mod_lines = ctx["mod_lines_chart"]
        mod_funcs = ctx["mod_funcs_chart"]
        alerts_html = ctx["alerts_html"]
        hotspots_html = ctx["hotspots_html"]
        refactor_html = ctx["refactor_html"]
        top_modules_html = ctx["top_modules_html"]
        modules = ctx["modules"]
        hotspots = ctx["hotspots"]
        refactoring = ctx["refactoring"]

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
    --orange: #f97316;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #f8fafc; --surface: #ffffff; --border: #e2e8f0;
      --text: #1e293b; --muted: #64748b;
    }}
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:2rem; }}
  h1 {{ font-size:1.5rem; margin-bottom:.5rem; }}
  h2 {{ font-size:1.1rem; color:var(--muted); margin:1.5rem 0 .75rem; border-bottom:1px solid var(--border); padding-bottom:.25rem; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:1rem; margin:1rem 0; }}
  .card {{ background:var(--surface); border:1px solid var(--border); border-radius:.5rem; padding:1rem; }}
  .card .value {{ font-size:1.8rem; font-weight:700; }}
  .card .label {{ color:var(--muted); font-size:.8rem; text-transform:uppercase; }}
  .chart-container {{ background:var(--surface); border:1px solid var(--border); border-radius:.5rem; padding:1rem; margin:1rem 0; }}
  .table-wrap {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  th {{ text-align:left; color:var(--muted); padding:.5rem; border-bottom:1px solid var(--border); white-space:nowrap; }}
  td {{ padding:.5rem; border-bottom:1px solid var(--border); }}
  .badge {{ padding:.15rem .5rem; border-radius:.25rem; font-size:.75rem; font-weight:600; }}
  .badge.critical {{ background:var(--red); color:#fff; }}
  .badge.error {{ background:var(--orange); color:#fff; }}
  .badge.warning {{ background:var(--yellow); color:#000; }}
  .badge.high {{ background:var(--red); color:#fff; }}
  .badge.medium {{ background:var(--yellow); color:#000; }}
  .badge.low {{ background:var(--green); color:#fff; }}
  tr.critical td {{ background:rgba(239,68,68,.08); }}
  tr.error td {{ background:rgba(249,115,22,.06); }}
  tr.warning td {{ background:rgba(234,179,8,.05); }}
  .health-indicator {{ display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:.5rem; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
  .three-col {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem; }}
  .evo-cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:.75rem; }}
  .evo-cards .card {{ text-align:center; }}
  .trend {{ font-size:.75rem; color:var(--muted); }}
  .lang-tag {{ display:inline-block; padding:.1rem .4rem; border-radius:.2rem; font-size:.7rem; font-weight:600; margin-right:.25rem; color:#fff; }}
  @media (max-width:768px) {{ .two-col,.three-col {{ grid-template-columns:1fr; }} }}
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
  &nbsp;·&nbsp; Primary language: <strong>{proj.get('language', 'unknown')}</strong>
  &nbsp;·&nbsp; {lang_summary}
</p>

<div class="grid">
  <div class="card"><div class="value">{stats.get('functions', 0):,}</div><div class="label">Functions</div></div>
  <div class="card"><div class="value">{stats.get('classes', 0):,}</div><div class="label">Classes</div></div>
  <div class="card"><div class="value">{stats.get('files', 0):,}</div><div class="label">Files</div></div>
  <div class="card"><div class="value">{stats.get('lines', 0):,}</div><div class="label">Lines</div></div>
  <div class="card"><div class="value">{len(lang['names'])}</div><div class="label">Languages</div></div>
  <div class="card"><div class="value">{cc_avg}</div><div class="label">Avg CC</div></div>
  <div class="card"><div class="value">{health.get('critical_count', 0)}</div><div class="label">Critical (CC≥{health.get('critical_limit', 10)})</div></div>
  <div class="card"><div class="value">{health.get('duplicates', 0)}</div><div class="label">Duplicates</div></div>
  <div class="card"><div class="value">{health.get('cycles', 0)}</div><div class="label">Cycles</div></div>
</div>

<div class="three-col">
  <div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Language Distribution</h2>
    <canvas id="langChart" height="200"></canvas>
  </div>
  <div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Largest Modules (lines)</h2>
    <canvas id="modLinesChart" height="200"></canvas>
  </div>
  <div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Most Complex Modules (functions)</h2>
    <canvas id="modFuncsChart" height="200"></canvas>
  </div>
</div>

<div class="two-col">
  {evo}
  <div>
    <h2>Top Modules ({len(modules)})</h2>
    <div class="card"><div class="table-wrap">
    <table>
      <thead><tr><th>Module</th><th>Path</th><th style="text-align:right">Lines</th><th style="text-align:right">Funcs</th><th style="text-align:right">Classes</th><th style="text-align:right">CC max</th></tr></thead>
      <tbody>{top_modules_html if top_modules_html else '<tr><td colspan="6" style="color:var(--muted)">No modules</td></tr>'}</tbody>
    </table>
    </div></div>
  </div>
</div>

<h2>Alerts ({len(health.get('alerts', []))})</h2>
<div class="card"><div class="table-wrap">
<table>
  <thead><tr><th>Severity</th><th>Target</th><th>Type</th><th>Value</th><th>Limit</th></tr></thead>
  <tbody>{alerts_html if alerts_html else '<tr><td colspan="5" style="color:var(--muted)">No alerts</td></tr>'}</tbody>
</table>
</div></div>

<div class="two-col">
<div>
<h2>Hotspots ({len(hotspots)})</h2>
<div class="card"><div class="table-wrap">
<table>
  <thead><tr><th>Function</th><th>Fan-out</th><th>Note</th></tr></thead>
  <tbody>{hotspots_html if hotspots_html else '<tr><td colspan="3" style="color:var(--muted)">No hotspots</td></tr>'}</tbody>
</table>
</div></div>
</div>

<div>
<h2>Refactoring Priorities ({len(refactoring.get('priorities', []))})</h2>
<div class="card"><div class="table-wrap">
<table>
  <thead><tr><th>#</th><th>Action</th><th>Impact</th><th>Effort</th></tr></thead>
  <tbody>{refactor_html if refactor_html else '<tr><td colspan="4" style="color:var(--muted)">No refactoring needed</td></tr>'}</tbody>
</table>
</div></div>
</div>
</div>

<footer>Generated by code2llm on {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>

<script>
{evo_script}

// Language distribution pie chart
const langCtx = document.getElementById('langChart').getContext('2d');
new Chart(langCtx, {{
  type: 'doughnut',
  data: {{
    labels: {lang['names']},
    datasets: [{{
      data: {lang['files']},
      backgroundColor: {lang['colors']},
      borderColor: 'var(--border)', borderWidth: 1
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'right', labels: {{ color: '#e2e8f0', font: {{size: 11}} }} }}
    }}
  }}
}});

// Module lines bar chart
const modLinesCtx = document.getElementById('modLinesChart').getContext('2d');
new Chart(modLinesCtx, {{
  type: 'bar',
  data: {{
    labels: {mod_lines['names']},
    datasets: [{{ label: 'Lines', data: {mod_lines['lines']},
      backgroundColor: '#3b82f6'
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

// Module functions bar chart
const modFuncsCtx = document.getElementById('modFuncsChart').getContext('2d');
new Chart(modFuncsCtx, {{
  type: 'bar',
  data: {{
    labels: {mod_funcs['names']},
    datasets: [{{ label: 'Functions', data: {mod_funcs['funcs']},
      backgroundColor: '#22c55e'
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

    @staticmethod
    def _render_evolution_section(evo: Dict) -> str:
        """Render evolution chart or metric cards depending on data points."""
        if evo["use_chart"]:
            return """<div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Evolution</h2>
    <canvas id="evoChart" height="200"></canvas>
  </div>"""

        entries = evo["entries"]
        if not entries:
            return """<div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Evolution</h2>
    <p style="color:var(--muted);">No history yet. Run analysis again to build trend data.</p>
  </div>"""

        last = entries[-1]
        prev = entries[-2] if len(entries) >= 2 else None
        cc = last.get("cc_avg", 0)
        crit = last.get("critical", 0)
        lines = last.get("lines", 0)

        def trend(cur, prv_val):
            if prv_val is None:
                return "→"
            if cur < prv_val:
                return "↓"
            if cur > prv_val:
                return "↑"
            return "→"

        cc_trend = trend(cc, prev.get("cc_avg") if prev else None)
        crit_trend = trend(crit, prev.get("critical") if prev else None)

        return f"""<div class="chart-container">
    <h2 style="border:none;margin:0 0 .5rem;">Evolution ({last.get('date', '?')})</h2>
    <div class="evo-cards">
      <div class="card"><div class="value">{cc}</div><div class="label">CC̄ {cc_trend}</div></div>
      <div class="card"><div class="value">{crit}</div><div class="label">Critical {crit_trend}</div></div>
      <div class="card"><div class="value">{lines}</div><div class="label">Lines</div></div>
    </div>
    <p class="trend" style="margin-top:.5rem;">Run analysis multiple times to build a trend chart (≥3 data points needed).</p>
  </div>"""

    @staticmethod
    def _render_evolution_script(evo: Dict) -> str:
        """Render Chart.js script for evolution line chart."""
        if not evo["use_chart"]:
            return "// Evolution chart disabled — fewer than 3 data points"
        return f"""const evoCtx = document.getElementById('evoChart').getContext('2d');
new Chart(evoCtx, {{
  type: 'line',
  data: {{
    labels: {evo["dates"]},
    datasets: [
      {{ label: 'CC avg', data: {evo["cc"]}, borderColor: '#3b82f6', tension: .3, yAxisID: 'y' }},
      {{ label: 'Critical', data: {evo["crit"]}, borderColor: '#ef4444', tension: .3, yAxisID: 'y1' }}
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
}});"""
