"""Run API tests and write an HTML report to test-results/api-test-report.html."""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
REPORT_DIR = ROOT / "test-results"
REPORT_PATH = REPORT_DIR / "api-test-report.html"


@dataclass
class ApiEndpoint:
    method: str
    path: str
    covered_by: list[str] = field(default_factory=list)


API_ENDPOINTS: list[ApiEndpoint] = [
    ApiEndpoint("POST", "/api/v1/runs", [
        "test_ingest_and_list_by_thread",
        "test_reject_invalid_payload",
        "test_upsert_run_end",
        "test_get_run_and_report_drilldown",
    ]),
    ApiEndpoint("GET", "/api/v1/runs/{run_id}", [
        "test_get_run_and_report_drilldown",
    ]),
    ApiEndpoint("GET", "/api/v1/threads/{thread_id}/runs", [
        "test_ingest_and_list_by_thread",
    ]),
    ApiEndpoint("GET", "/api/v1/traces/{trace_id}/runs", [
        "test_ingest_and_list_by_thread",
        "test_upsert_run_end",
    ]),
    ApiEndpoint("GET", "/api/v1/report/users/{user_id}/threads", [
        "test_get_run_and_report_drilldown",
    ]),
    ApiEndpoint("GET", "/health"),
    ApiEndpoint("GET", "/", ["test_root_redirects_to_report"]),
    ApiEndpoint("GET", "/report", ["test_report_page", "test_get_run_and_report_drilldown"]),
    ApiEndpoint("GET", "/report/users/{user_id}", ["test_get_run_and_report_drilldown"]),
    ApiEndpoint("GET", "/report/threads/{thread_id}", ["test_get_run_and_report_drilldown"]),
    ApiEndpoint("GET", "/report/runs/{run_id}", ["test_get_run_and_report_drilldown"]),
    ApiEndpoint("GET", "/simulator", ["test_simulator_page"]),
    ApiEndpoint("POST", "/api/v1/simulator/run"),
    ApiEndpoint("GET", "/api/v1/simulator/status"),
]


@dataclass
class TestResult:
    nodeid: str
    name: str
    file: str
    outcome: str
    duration: float
    detail: str | None = None


class ResultCollector:
    def __init__(self) -> None:
        self.results: list[TestResult] = []

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when != "call":
            return
        nodeid = report.nodeid
        file_part, _, name = nodeid.partition("::")
        self.results.append(
            TestResult(
                nodeid=nodeid,
                name=name,
                file=Path(file_part).name,
                outcome=report.outcome,
                duration=report.duration,
                detail=str(report.longrepr) if report.failed or report.skipped else None,
            )
        )


def discover_test_scripts() -> list[Path]:
    return sorted(TESTS_DIR.glob("test_*.py"))


def build_html(
    scripts: list[Path],
    results: list[TestResult],
    exit_code: int,
) -> str:
    passed = [r for r in results if r.outcome == "passed"]
    failed = [r for r in results if r.outcome == "failed"]
    skipped = [r for r in results if r.outcome == "skipped"]
    result_by_name = {r.name: r for r in results}
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    overall = "PASSED" if exit_code == 0 else "FAILED"
    overall_class = "pass" if exit_code == 0 else "fail"

    api_rows: list[str] = []
    covered_count = 0
    for endpoint in API_ENDPOINTS:
        if endpoint.covered_by:
            covered_count += 1
            test_cells = []
            for test_name in endpoint.covered_by:
                result = result_by_name.get(test_name)
                if result is None:
                    badge = '<span class="badge unknown">not run</span>'
                elif result.outcome == "passed":
                    badge = '<span class="badge pass">passed</span>'
                else:
                    badge = f'<span class="badge fail">{html.escape(result.outcome)}</span>'
                test_cells.append(f"<li><code>{html.escape(test_name)}</code> {badge}</li>")
            tests_html = "<ul class=\"test-list\">" + "".join(test_cells) + "</ul>"
            status = '<span class="badge pass">covered</span>'
        else:
            tests_html = '<span class="muted">No automated test</span>'
            status = '<span class="badge warn">uncovered</span>'
        api_rows.append(
            "<tr>"
            f"<td><code>{html.escape(endpoint.method)}</code></td>"
            f"<td><code>{html.escape(endpoint.path)}</code></td>"
            f"<td>{status}</td>"
            f"<td>{tests_html}</td>"
            "</tr>"
        )

    detail_rows: list[str] = []
    for result in results:
        outcome_class = result.outcome
        detail_block = ""
        if result.detail:
            detail_block = (
                f'<pre class="detail">{html.escape(result.detail)}</pre>'
            )
        detail_rows.append(
            "<tr>"
            f"<td><code>{html.escape(result.file)}</code></td>"
            f"<td><code>{html.escape(result.name)}</code></td>"
            f'<td><span class="badge {outcome_class}">{html.escape(result.outcome)}</span></td>'
            f"<td>{result.duration:.3f}s</td>"
            f"<td>{detail_block}</td>"
            "</tr>"
        )

    script_items = "".join(
        f"<li><code>{html.escape(path.relative_to(ROOT).as_posix())}</code></li>"
        for path in scripts
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentSmith-Trace API Test Report</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --card: #ffffff;
      --text: #1f2933;
      --muted: #6b7280;
      --border: #d9e2ec;
      --pass: #0f9d58;
      --fail: #d93025;
      --warn: #f9a825;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ font-size: 1.75rem; }}
    h2 {{ font-size: 1.2rem; margin-top: 28px; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px 20px;
      margin-bottom: 16px;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }}
    .metric {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      background: #fafbfc;
    }}
    .metric .label {{ color: var(--muted); font-size: 0.9rem; }}
    .metric .value {{ font-size: 1.5rem; font-weight: 700; }}
    .overall {{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      font-weight: 700;
      color: #fff;
      background: var(--{overall_class});
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      border: 1px solid var(--border);
      padding: 10px 12px;
      vertical-align: top;
      text-align: left;
    }}
    th {{ background: #eef2f7; }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 0.9em;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 600;
      color: #fff;
    }}
    .badge.pass {{ background: var(--pass); }}
    .badge.fail {{ background: var(--fail); }}
    .badge.warn {{ background: var(--warn); color: #1f2933; }}
    .badge.skipped {{ background: #9aa5b1; }}
    .badge.unknown {{ background: #9aa5b1; }}
    .muted {{ color: var(--muted); }}
    ul {{ margin: 0; padding-left: 20px; }}
    .test-list {{ margin: 0; padding-left: 18px; }}
    pre.detail {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #111827;
      color: #f9fafb;
      padding: 10px;
      border-radius: 6px;
      font-size: 0.82rem;
      max-height: 240px;
      overflow: auto;
    }}
    .meta {{ color: var(--muted); font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>AgentSmith-Trace API Test Report</h1>
      <p class="meta">Generated at {generated_at}</p>
      <p>Overall result: <span class="overall">{overall}</span></p>
    </div>

    <div class="card">
      <h2>Test Scripts</h2>
      <div class="summary-grid">
        <div class="metric">
          <div class="label">Test scripts</div>
          <div class="value">{len(scripts)}</div>
        </div>
        <div class="metric">
          <div class="label">Test cases</div>
          <div class="value">{len(results)}</div>
        </div>
        <div class="metric">
          <div class="label">Passed</div>
          <div class="value">{len(passed)}</div>
        </div>
        <div class="metric">
          <div class="label">Failed</div>
          <div class="value">{len(failed)}</div>
        </div>
        <div class="metric">
          <div class="label">Skipped</div>
          <div class="value">{len(skipped)}</div>
        </div>
      </div>
      <ul>{script_items}</ul>
    </div>

    <div class="card">
      <h2>API Coverage</h2>
      <div class="summary-grid">
        <div class="metric">
          <div class="label">Total API routes</div>
          <div class="value">{len(API_ENDPOINTS)}</div>
        </div>
        <div class="metric">
          <div class="label">Covered routes</div>
          <div class="value">{covered_count}</div>
        </div>
        <div class="metric">
          <div class="label">Uncovered routes</div>
          <div class="value">{len(API_ENDPOINTS) - covered_count}</div>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Path</th>
            <th>Coverage</th>
            <th>Tests</th>
          </tr>
        </thead>
        <tbody>
          {"".join(api_rows)}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Detailed Test Results</h2>
      <table>
        <thead>
          <tr>
            <th>Script</th>
            <th>Test</th>
            <th>Result</th>
            <th>Duration</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {"".join(detail_rows)}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


def main() -> int:
    scripts = discover_test_scripts()
    collector = ResultCollector()
    exit_code = pytest.main(
        [str(TESTS_DIR / "test_api.py"), "-q", "--tb=short"],
        plugins=[collector],
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        build_html(scripts, collector.results, exit_code),
        encoding="utf-8",
    )
    print(f"Report written to {REPORT_PATH}")
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
