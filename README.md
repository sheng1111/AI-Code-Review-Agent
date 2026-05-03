# 🤖 AI Code Review System

GitHub Actions based AI code review. The default setup uses OpenAI `gpt-5.4-nano`, Flex Processing, and a concise output contract that only reports actionable issues backed by diff evidence.

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
    "name": "gpt-5.4-nano",
    "fallback_models": ["gpt-5.4-mini", "gpt-5.4"],
    "api_mode": "responses",
    "reasoning_effort": "medium",
    "verbosity": "low",
    "service_tier": "flex",
    "max_tokens": 32768,
    "timeout": 900
  },
  "projects": {
    "enabled_repos": ["*"]
  }
}
```

`temperature` is intentionally not part of the default config. The OpenAI Responses API still documents sampling parameters, but GPT-5.4 review behavior is better controlled with `reasoning_effort`, `verbosity`, and a strict output contract.

## Flex Processing

`service_tier` defaults to `flex`, which is a good fit for asynchronous GitHub Actions review: lower cost, slower responses, and occasional resource unavailability. For higher reliability, use:

```json
{
  "model": {
    "service_tier": "auto"
  }
}
```

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
```

## Advanced Config

See [CONFIG.md](CONFIG.md).
