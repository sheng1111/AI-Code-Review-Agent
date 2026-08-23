#!/usr/bin/env python3
"""Deterministic orchestration benchmark for large-diff review processing."""

import time
from statistics import median

import ai_code_review as review


def make_workload(file_count=8):
    """Build a representative eight-file diff without network access."""
    files = []
    parts = []
    for index in range(file_count):
        filename = f"src/file_{index}.py"
        files.append({"filename": filename, "additions": 100, "deletions": 20})
        parts.append(
            f"diff --git a/{filename} b/{filename}\n"
            f"--- a/{filename}\n+++ b/{filename}\n@@ -1 +1 @@\n-old\n+new"
        )
    commit_info = {
        "files": files,
        "commit": {
            "author": {"name": "Benchmark", "date": "2026-08-23"},
            "message": "deterministic benchmark",
        },
    }
    return "\n".join(parts), commit_info


def main():
    """Run the benchmark with a local no-op LLM stub."""
    diff, commit_info = make_workload()
    original_call = review.call_llm_api
    call_count = 0

    def local_llm(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return "NO_ACTIONABLE_FINDINGS\n未發現需要修改的問題。"

    review.call_llm_api = local_llm
    samples = []
    try:
        for _ in range(100):
            started = time.perf_counter()
            review.review_large_diff_in_chunks(diff, commit_info)
            samples.append(time.perf_counter() - started)
    finally:
        review.call_llm_api = original_call

    samples.sort()
    print(f"version={review.APP_VERSION}")
    print("workload=large_diff_8_files")
    print(f"iterations={len(samples)}")
    print(f"llm_calls_per_iteration={call_count / len(samples):.0f}")
    print(f"median_seconds={median(samples):.6f}")
    print(f"p95_seconds={samples[int(len(samples) * 0.95) - 1]:.6f}")


if __name__ == "__main__":
    main()
