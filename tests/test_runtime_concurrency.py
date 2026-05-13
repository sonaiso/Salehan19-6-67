from __future__ import annotations

import threading

from mcd.api.observability import APILogTrace, TraceStore


def test_trace_store_concurrency_no_race():
    store = TraceStore()
    errors: list[Exception] = []

    def writer(worker_id: int) -> None:
        try:
            for i in range(50):
                store.record(
                    APILogTrace(
                        request_id=f"{worker_id}-{i}",
                        path="/v1/health",
                        method="GET",
                        status_code=200,
                        execution_time_ms=1.0,
                        replay_id=f"rp-{worker_id}-{i}",
                    )
                )
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(store.all()) <= store._MAX_TRACES

