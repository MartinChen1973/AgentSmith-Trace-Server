"""Quick inspect agentsmith_trace.db for call-stack debugging."""
import json
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "agentsmith_trace.db"
if not db.exists():
    print(f"No DB at {db}")
    raise SystemExit(1)

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

users = conn.execute(
    """
    SELECT DISTINCT json_extract(metadata_json, '$.user_id') AS uid, COUNT(*) AS n
    FROM runs GROUP BY uid ORDER BY n DESC
    """
).fetchall()
print("=== user_ids ===")
for u in users:
    print(f"  {u['uid']}: {u['n']} runs")

threads = conn.execute(
    """
    SELECT json_extract(metadata_json, '$.thread_id') AS tid,
           json_extract(metadata_json, '$.user_id') AS uid,
           COUNT(*) AS n
    FROM runs GROUP BY tid ORDER BY n DESC LIMIT 5
    """
).fetchall()
print("=== threads ===")
for t in threads:
    print(f"  {t['tid']} ({t['uid']}): {t['n']} runs")

tid = threads[0]["tid"] if threads else None
if tid:
    rows = conn.execute(
        """
        SELECT run_id, parent_run_id, name, run_type, metadata_json
        FROM runs
        WHERE json_extract(metadata_json, '$.thread_id') = ?
        ORDER BY start_time
        """,
        (tid,),
    ).fetchall()
    print(f"=== thread {tid} ({len(rows)} runs) ===")
    for r in rows:
        meta = json.loads(r["metadata_json"])
        kind = meta.get("activity_kind", "")
        phase = meta.get("phase", "")
        parent = (r["parent_run_id"] or "NULL")[:8]
        print(
            f"  {r['run_id'][:8]} parent={parent} "
            f"name={r['name']} kind={kind} phase={phase}"
        )

    subagents = [
        r for r in rows
        if json.loads(r["metadata_json"]).get("activity_kind") == "subagent_task"
    ]
    if len(subagents) >= 2:
        ids = [r["run_id"] for r in subagents]
        print("subagent run_ids:", [x[:8] for x in ids])
        print("reuse same id:", ids[0] == ids[1] if len(ids) >= 2 else "n/a")
