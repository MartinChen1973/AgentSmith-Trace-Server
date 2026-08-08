"""Print call-stack forest for a thread."""
import json
import sqlite3
import sys
from pathlib import Path

from agentsmith_trace_server.report_call_stack import activity_kind, build_stack_forest

db = Path(__file__).resolve().parents[1] / "agentsmith_trace.db"
tid = sys.argv[1] if len(sys.argv) > 1 else None

conn = sqlite3.connect(db)
if not tid:
    tid = conn.execute(
        """
        SELECT json_extract(metadata_json, '$.thread_id')
        FROM runs GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1
        """
    ).fetchone()[0]

rows = conn.execute(
    """
    SELECT run_id, parent_run_id, name, run_type, start_time,
           metadata_json, inputs_json, outputs_json, status
    FROM runs
    WHERE json_extract(metadata_json, '$.thread_id') = ?
    ORDER BY start_time
    """,
    (tid,),
).fetchall()

runs = []
for r in rows:
    runs.append(
        {
            "run_id": r[0],
            "parent_run_id": r[1],
            "name": r[2],
            "run_type": r[3],
            "start_time": r[4],
            "metadata": json.loads(r[5]),
            "inputs": json.loads(r[6]),
            "outputs": json.loads(r[7]),
            "status": r[8],
        }
    )


def show(node, indent=0) -> None:
    m = node.run
    kind = activity_kind(m)
    print(f"{'  ' * indent}{node.role}: {m['name']} ({kind})")
    for ch in node.children:
        show(ch, indent + 1)


forest = build_stack_forest(runs)
print(f"thread {tid}")
print(f"forest roots: {len(forest)}")
for n in forest:
    show(n)
