# Changelog

## 1.0.0 - 2026-08-23

- Use `gpt-5.6-luna` with low reasoning effort and Flex Processing by default.
- Fall back from unavailable Flex capacity to standard project routing with bounded retry and jitter.
- Default to Traditional Chinese and accept structurally valid BCP 47 output-language tags.
- Review all bounded large-diff chunks, including JSON, YAML, and GitHub Actions changes.
- Filter ignored assets before model calls and reuse HTTP connections and commit metadata.
- Remove ineffective per-result sleeps and document reproducible before/after performance results.
- Add unit tests, configuration validation, and current GitHub Actions dependencies.
- Propagate review failures to GitHub Actions and report the actual job status.
