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

- `model.name`: `gpt-5.4-nano`
- `model.fallback_models`: `["gpt-5.4-mini", "gpt-5.4"]`
- `model.api_mode`: `responses`
- `model.reasoning_effort`: `medium`
- `model.verbosity`: `low`
- `model.service_tier`: `flex`
- `model.max_tokens`: `32768`
- `model.timeout`: `900`
- `projects.enabled_repos`: `["*"]`
- `review.response_language`: `zh-TW`

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
    "name": "gpt-5.4-mini",
    "fallback_models": ["gpt-5.4"],
    "service_tier": "auto",
    "reasoning_effort": "high",
    "verbosity": "low"
  }
}
```

`temperature` is intentionally omitted from the default config. The Responses API still documents `temperature`, but GPT-5-class review quality is usually better controlled with `reasoning_effort`, `verbosity`, and a precise output contract.

## Flex Processing

`service_tier: "flex"` is enabled by default to reduce cost for asynchronous code review. Flex can be slower and may occasionally return resource-unavailable errors, so the default timeout is 900 seconds.

Use `"auto"` if you prefer reliability over cost.
