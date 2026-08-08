"""List ChatOpenAI runs in agentsmith_trace.db."""
import json
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "agentsmith_trace.db"
conn = sqlite3.connect(db)
rows = conn.execute(
    """
    SELECT run_id, parent_run_id, start_time, outputs_json, metadata_json
    FROM runs WHERE name = 'ChatOpenAI' ORDER BY start_time
    """
).fetchall()
for r in rows:
    out = json.loads(r[3])
    meta = json.loads(r[4])
    content = str(out.get("content") or "")[:80].replace("\n", " ")
    model = meta.get("model", "")
    print(f"{r[0][:16]} parent={str(r[1] or '')[:16]} {r[2][:22]} model={model!r} content={content!r}")
print("total", len(rows))
if rows:
    out = json.loads(rows[0][3])
    print("sample outputs keys:", list(out.keys()))
    print(json.dumps(out, indent=2)[:1200])
