# Configuration Guide

`config.json` is optional. The default setup is designed for quick GitHub Actions onboarding: add secrets, enable Actions, and it reviews the current repository on push plus all repositories accessible by `GH_TOKEN` during scheduled scans.

## Minimal Configuration

```json
{
  "review": {
    "response_language": "zh-TW"
  }
}
```

## Defaults

- `model.name`: `gpt-5.6-luna`
- `model.fallback_models`: `[]`
- `model.api_mode`: `responses`
- `model.reasoning_effort`: `low`
- `model.verbosity`: `low`
- `model.service_tier`: `flex`
- `model.flex_fallback_to_auto`: `true`
- `model.max_retries`: `3`
- `model.retry_backoff_seconds`: `1.0`
- `model.max_tokens`: `16384`
- `model.timeout`: `900`
- `projects.enabled_repos`: `["*"]`
- `review.response_language`: `zh-TW`
- `review.chunk_concurrency`: `2`

## Optional Repository Allowlist

By default, scheduled scans monitor all repositories accessible by `GH_TOKEN`.

Set an allowlist only when you want to restrict monitoring:

```json
{
  "projects": {
    "enabled_repos": ["owner/repo1", "owner/repo2"]
  }
}
```

## Optional Model Overrides

```json
{
  "model": {
    "name": "gpt-5.6-luna",
    "fallback_models": [],
    "service_tier": "auto",
    "reasoning_effort": "high",
    "verbosity": "low"
  }
}
```

`temperature` is intentionally omitted from the default config. GPT-5.6 review quality is controlled with `reasoning_effort`, `verbosity`, and a precise output contract.

## Flex Processing

`service_tier: "flex"` is enabled by default to reduce cost for asynchronous code review. Flex can be slower and may occasionally return resource-unavailable errors, so the default timeout is 900 seconds. With `flex_fallback_to_auto: true`, a Flex capacity error falls back to `auto` after bounded retries.

Use `"auto"` if you prefer reliability over cost.

## BCP 47 Output Language

`review.response_language` accepts structurally valid BCP 47 tags rather than a fixed language list. Examples include `zh-TW`, `en-US`, `zh-Hant-TW`, `sr-Latn-RS`, `es-419`, and private-use tags such as `x-review`.

## Retry and Chunk Controls

- `model.max_retries`: bounded retries per model and service tier, from 1 to 10.
- `model.retry_backoff_seconds`: exponential-backoff base, from 0 to 60 seconds; server `Retry-After` takes precedence.
- `review.chunk_concurrency`: concurrent large-diff chunks, from 1 to 16.
- `review.max_diff_size`: maximum characters sent in one review chunk. All reviewable chunks are processed; content beyond the first chunk is no longer silently dropped.

Official references: [GPT-5.6 Luna model](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and [Flex Processing](https://developers.openai.com/api/docs/guides/flex-processing).
