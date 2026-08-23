# Performance Baseline and Results

Version 1.0.0 includes a deterministic local benchmark for review orchestration. It replaces network and model work with a no-op stub so the measurement isolates application overhead. It is not an end-to-end OpenAI latency benchmark.

## Reproduce

```bash
python3 scripts/benchmark_review.py
```

Workload: one synthetic large diff containing eight Python files, executed on macOS with Python 3.9.6. The pre-change baseline was captured from commit `4b85655`; the post-change result uses 100 iterations.

| Metric | Before | After | Change |
| --- | ---: | ---: | ---: |
| Orchestration time | 4.0383 s | 0.000077 s median | 99.998% lower |
| Time spent in fixed sleeps | 4.037 s | 0 s | removed |
| LLM calls for this workload | 9 | 1 | 88.9% fewer |
| GitHub commit-info requests per reviewed commit | 2 | 1 | 50% fewer |

The post-change p95 orchestration time was 0.000096 seconds. Real workflow time is dominated by GitHub and OpenAI network latency, so production improvements will vary.

## Bottlenecks Found

1. The result collector slept 0.5 seconds after every completed file review even though every request had already been submitted. This added four seconds to an eight-file review without enforcing a request rate.
2. Large commits used one evidence-free overview call plus up to eight per-file calls. Files outside that top-eight selection were not reviewed.
3. Diffs between 150,000 and 300,000 characters followed the single-call path but were truncated to 150,000 characters, silently dropping the remainder.
4. Issue creation fetched commit metadata that the review path had already fetched.
5. Module-level `requests.get` and `requests.post` calls created short-lived sessions and could not consistently reuse HTTP connections.

## Improvements

- Reviewable diff sections are parsed once, ignored documentation/assets are removed before token use, and every remaining section is packed into bounded chunks.
- Chunk calls run with bounded concurrency and no collector sleeps.
- Commit metadata is passed through to issue creation.
- Per-thread Requests sessions reuse connections and safely support concurrent repository scans.
- Flex capacity errors can fall back to standard project routing; transient failures use bounded exponential backoff with jitter and honor `Retry-After`.

The quality/cost tradeoff should also be evaluated against representative real diffs before changing `reasoning_effort` or chunk size. This repository does not make paid API calls during its local benchmark or unit tests.
