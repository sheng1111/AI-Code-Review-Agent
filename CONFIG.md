# Configuration Guide

This document explains all configuration options in `config.json`.

## Model Configuration (`model`)

- **`name`**: Primary LLM model for code review
- **`fallback_models`**: Alternative models to try if primary fails
- **`max_tokens`**: Maximum tokens for model response (increase for longer reviews)
- **`temperature`**: Model temperature (0.0 = deterministic, 1.0 = creative)
- **`timeout`**: API request timeout in seconds

## Project Configuration (`projects`)

- **`enabled_repos`**: List of repositories to enable AI review for (use `["*"]` for all repos)
- **`default_repo`**: Default repository for manual testing

## Review Configuration (`review`)

- **`max_diff_size`**: Maximum diff size to process in single review (characters)
- **`large_diff_threshold`**: Threshold for large changes requiring chunked analysis
- **`chunk_max_tokens`**: Max tokens per chunk in large diff analysis
- **`max_files_detail`**: Maximum number of files to review in detail for large changes
- **`overview_max_tokens`**: Max tokens for overview analysis of large changes
- **`response_language`**: Response language code (see supported languages below)

## Filter Configuration (`filters`)

- **`ignored_extensions`**: File extensions to ignore during review
- **`ignored_paths`**: Directory paths to ignore during review
- **`code_extensions`**: File extensions considered as code files

## Prompt Configuration (`prompts`)

- **`include_line_numbers`**: Include line numbers in code analysis when possible
- **`detailed_analysis`**: Provide detailed analysis for each section
- **`security_focus`**: Focus on security vulnerabilities
- **`performance_analysis`**: Include performance analysis

## Supported Languages

| Code | Language | Example |
|------|----------|---------|
| `zh-TW` | Traditional Chinese | 繁體中文 |
| `zh-CN` | Simplified Chinese | 简体中文 |
| `en` | English | English |
| `ja` | Japanese | 日本語 |
| `ko` | Korean | 한국어 |
| `fr` | French | Français |
| `de` | German | Deutsch |
| `es` | Spanish | Español |
| `pt` | Portuguese | Português |
| `ru` | Russian | Русский |

## Configuration Validation

The system automatically validates the configuration file structure and values on startup, including:

### Structure Validation
- Checks that all required configuration sections exist
- Validates data types for each field
- Ensures required fields are not empty

### Value Validation
- `model.max_tokens` > 0
- `model.temperature` within 0.0-2.0 range
- `model.timeout` > 0
- All `review` section numeric parameters > 0
- `response_language` must be a supported language code
- `enabled_repos` format must be `owner/repo` or `*`
- File extensions must start with `.`

### Validation Error Examples
```
Configuration validation error: Missing required field: model.name
Configuration validation error: model.temperature must be between 0.0 and 2.0
Configuration validation error: Repository 'invalid-repo' must be in 'owner/repo' format or '*' for all repos
Configuration validation error: File extension 'txt' must start with '.'
```

## Troubleshooting

### JSON Syntax Errors
If the configuration file has JSON syntax errors, the program will report the error and exit on startup.

### Configuration Validation Failures
The system will display specific validation error messages to help you fix configuration issues.

### Model Connection Issues
Check that `OPENAI_BASE_URL` and `OPENAI_KEY` environment variables are correctly set.

### Permission Issues
Ensure that `GH_TOKEN` has sufficient permissions to access target repositories. 