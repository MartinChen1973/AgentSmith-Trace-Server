from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from agentsmith_trace_server.api import create_app
from agentsmith_trace_server.models import RunEvent, RunStatus, RunType


def test_ingest_and_list_by_thread(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    trace_id = uuid4()
    run_id = uuid4()
    thread_id = "thread_test"

    event = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        inputs={"messages": [{"role": "user", "content": "hello"}]},
        outputs={"content": "hi"},
        metadata={"user_id": "usr_1", "thread_id": thread_id},
    )

    response = client.post("/api/v1/runs", json=event.model_dump(mode="json"))
    assert response.status_code == 201
    assert response.json()["run_id"] == str(run_id)

    thread_runs = client.get(f"/api/v1/threads/{thread_id}/runs")
    assert thread_runs.status_code == 200
    body = thread_runs.json()
    assert body["count"] == 1
    assert body["runs"][0]["inputs"]["messages"][0]["content"] == "hello"

    trace_runs = client.get(f"/api/v1/traces/{trace_id}/runs")
    assert trace_runs.status_code == 200
    assert trace_runs.json()["count"] == 1


def test_reject_invalid_payload(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    response = client.post("/api/v1/runs", json={"name": "incomplete"})
    assert response.status_code == 422


def test_upsert_run_end(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    trace_id = uuid4()
    run_id = uuid4()

    start = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.PENDING,
        start_time=datetime.now(timezone.utc),
        inputs={"messages": [{"role": "user", "content": "ping"}]},
        metadata={"thread_id": "t1"},
    )
    client.post("/api/v1/runs", json=start.model_dump(mode="json"))

    end = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.SUCCESS,
        start_time=start.start_time,
        end_time=datetime.now(timezone.utc),
        outputs={"content": "pong"},
        metadata={"thread_id": "t1"},
    )
    client.post("/api/v1/runs", json=end.model_dump(mode="json"))

    runs = client.get(f"/api/v1/traces/{trace_id}/runs").json()["runs"]
    assert runs[0]["status"] == "success"
    assert runs[0]["outputs"]["content"] == "pong"
    assert runs[0]["inputs"]["messages"][0]["content"] == "ping"


def test_report_page(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    response = client.get("/report")
    assert response.status_code == 200
    assert "AgentSmith-Trace" in response.text
    assert "#0f1419" in response.text
    assert "Segoe UI" in response.text
    assert "整体日志" in response.text or "暂无数据" in response.text
    assert "text/html" in response.headers.get("content-type", "")


def test_simulator_page(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    response = client.get("/simulator")
    assert response.status_code == 200
    assert "Run sample test" in response.text


def test_root_redirects_to_report(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/report"


def test_get_run_and_report_drilldown(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    trace_id = uuid4()
    run_id = uuid4()
    thread_id = "thread_detail"
    user_id = "usr_detail"

    event = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        inputs={
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "system prompt"}],
                },
                {"role": "user", "content": "hello"},
            ]
        },
        outputs={"content": "hi", "token_usage": {"total_tokens": 10}},
        metadata={"user_id": user_id, "thread_id": thread_id, "lc_agent_name": "orchestrator"},
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    run_resp = client.get(f"/api/v1/runs/{run_id}")
    assert run_resp.status_code == 200
    assert run_resp.json()["outputs"]["content"] == "hi"

    threads_resp = client.get(f"/api/v1/report/users/{user_id}/threads")
    assert threads_resp.status_code == 200
    assert threads_resp.json()["count"] == 1
    assert threads_resp.json()["threads"][0]["thread_id"] == thread_id

    report = client.get("/report")
    assert report.status_code == 200
    assert "整体日志" in report.text
    assert thread_id in report.text
    assert f"thread_id={thread_id}" in report.text
    assert "调用栈" in report.text
    assert "call-stack-root" in report.text
    assert "thread-link active" in report.text
    assert "hello" in report.text

    selected = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert selected.status_code == 200
    assert "hello" in selected.text
    assert "hi" in selected.text
    assert "会话" in selected.text
    assert "Input messages" in selected.text
    assert "thread-link active" in selected.text
    assert "chat-row-user" in selected.text
    assert "chat-row-assistant" in selected.text
    assert "chat-block" in selected.text
    assert "chat-avatar-user" in selected.text
    assert "chat-avatar-assistant" in selected.text
    assert "bubble-expandable" in selected.text
    assert "data-chat-expand-all" in selected.text
    assert "setAllExpanded" in selected.text
    assert '<span class="speaker">orchestrator</span>' in selected.text

    user_redirect = client.get(f"/report/users/{user_id}", follow_redirects=False)
    assert user_redirect.status_code in (307, 308)
    assert f"user_id={user_id}" in user_redirect.headers["location"]

    thread_redirect = client.get(f"/report/threads/{thread_id}", follow_redirects=False)
    assert thread_redirect.status_code in (307, 308)
    assert f"thread_id={thread_id}" in thread_redirect.headers["location"]

    run_page = client.get(f"/report/runs/{run_id}")
    assert run_page.status_code == 200
    assert "hello" in run_page.text
    assert "orchestrator" in run_page.text

    missing = client.get(f"/api/v1/runs/{uuid4()}")
    assert missing.status_code == 404
