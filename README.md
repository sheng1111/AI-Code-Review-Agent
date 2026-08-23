# 🤖 AI Code Review System

GitHub Actions based AI code review, version 1.0.0. The default setup uses OpenAI `gpt-5.6-luna`, low reasoning effort, Flex Processing, and a concise output contract that only reports actionable issues backed by diff evidence.

## Quick Start

1. Put this project in your repository.
2. Add GitHub Actions secrets:
   - `GH_TOKEN`: GitHub PAT with repository read access and issue write access.
   - `OPENAI_KEY`: OpenAI API key.
3. Enable GitHub Actions.
4. Push code. Review results are created as Issues with the `ai-code-review` label.

`OPENAI_BASE_URL` is optional and defaults to `https://api.openai.com/v1`. Set it only for self-hosted or OpenAI-compatible providers.

## Default Behavior

- Push workflow reviews commits in the current repository.
- Scheduled workflow scans every repository accessible by `GH_TOKEN`.
- No `default_repo` setting is needed.
- No repository list is needed; unspecified means monitor all accessible repositories.
- Set `projects.enabled_repos` only when you want an allowlist.
- If no actionable issue is found, the output is exactly: `未發現需要修改的問題。`

## Minimal Config

`config.json` can be as small as:

```json
{
  "review": {
    "response_language": "zh-TW"
  }
}
```

You can also remove `config.json`; built-in defaults will be used.

## Built-In Model Defaults

```json
{
  "model": {
    "name": "gpt-5.6-luna",
    "fallback_models": [],
    "api_mode": "responses",
    "reasoning_effort": "low",
    "verbosity": "low",
    "service_tier": "flex",
    "flex_fallback_to_auto": true,
    "max_retries": 3,
    "retry_backoff_seconds": 1.0,
    "max_tokens": 16384,
    "timeout": 900
  },
  "projects": {
    "enabled_repos": ["*"]
  }
}
```

`temperature` is intentionally not part of the default config. GPT-5.6 review behavior is controlled with `reasoning_effort`, `verbosity`, and a strict output contract.

## Flex Processing

`service_tier` defaults to `flex`, which is a good fit for asynchronous GitHub Actions review: lower cost, slower responses, and occasional resource unavailability. By default a Flex resource-unavailable response is retried with `service_tier: "auto"`; disable this with `flex_fallback_to_auto: false` when cost is more important than completion. To always use standard project routing, use:

```json
{
  "model": {
    "service_tier": "auto"
  }
}
```

## Output Language

`review.response_language` defaults to `zh-TW`. Any structurally valid BCP 47 language tag is accepted, including `en-US`, `zh-Hant-TW`, `sr-Latn-RS`, and `es-419`. Code, identifiers, paths, and severity labels remain unchanged.

## Repository Allowlist

Only set this when you do not want all accessible repositories monitored:

```json
{
  "projects": {
    "enabled_repos": [
      "owner/repo1",
      "owner/repo2"
    ]
  }
}
```

## Review Output

Each actionable finding includes:

- `位置`: file and line/hunk
- `證據`: concrete diff evidence
- `影響`: concrete failure mode
- `修法`: exact implementation direction
- `驗證`: command or test case
- `AI_AGENT_FIX_PROMPT`: direct repair instruction for an AI coding agent

If there is no issue, the review does not invent one.

## Local Validation

```bash
python3 scripts/test_config.py
python3 -m unittest discover -s tests -v
python3 scripts/benchmark_review.py
```

The workflows use current `actions/checkout@v7` and `actions/setup-python@v7`, upgrade pip, and install the latest compatible Requests 2.x release. See [PERFORMANCE.md](PERFORMANCE.md) for the reproducible before/after benchmark and bottleneck analysis.

## Advanced Config

See [CONFIG.md](CONFIG.md).
