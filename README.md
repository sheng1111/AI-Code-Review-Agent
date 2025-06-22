# 🤖 AI Code Review System

An automated code review tool based on large language models, providing professional and comprehensive code quality analysis. Supports multi-repository monitoring, automated reviews, and intelligent analysis.

## ✨ Core Features

### 🔍 Multiple Trigger Modes

#### 1. Push Trigger Mode (Single Repository)
- **Trigger Condition**: Automatically executed when pushing to any branch
- **Smart Filtering**: Automatically skips documentation changes (`.md`, `.txt`) and merge commits
- **Manual Trigger Support**: Can specify specific commit SHA for review

#### 2. Scheduled Scan Mode (Multi-Repository)
- **Scheduled Execution**: Daily automatic scan at 2:00 AM UTC+8 (6:00 PM UTC)
- **Multi-Repository Support**: Simultaneously monitors all repositories in the configuration list
- **Smart Limiting**: Process up to 3 latest commits per repository
- **Avoid Duplication**: Automatically skips already reviewed commits

### 📊 Professional Analysis Dimensions
- **Security Analysis**: SQL injection, XSS, CSRF vulnerability detection
- **Performance Evaluation**: Algorithm complexity, database optimization, memory usage
- **Code Quality**: Readability, maintainability, SOLID principles checking
- **Test Coverage**: Unit test suggestions, boundary condition checking
- **Best Practices**: Language-specific standards, design pattern evaluation

### 🌍 Multi-Language Response Support
Supports code review reports in 10 languages:
- 🇹🇼 Traditional Chinese (`zh-TW`)
- 🇨🇳 Simplified Chinese (`zh-CN`)
- 🇺🇸 English (`en`)
- 🇯🇵 Japanese (`ja`)
- 🇰🇷 Korean (`ko`)
- 🇫🇷 French (`fr`)
- 🇩🇪 German (`de`)
- 🇪🇸 Spanish (`es`)
- 🇵🇹 Portuguese (`pt`)
- 🇷🇺 Russian (`ru`)

### ⚡ Performance Optimization Features
- **Parallel Processing**: Multi-file simultaneous review for improved processing speed
- **Smart Segmentation**: Large changes automatically segmented (when exceeding 300KB)
- **Configuration Caching**: Reduces redundant configuration loading
- **API Rate Control**: Avoids frequency limitations
- **Fallback Models**: Supports multiple backup LLM models for service reliability

## 📂 Project Structure

```
PR-Agent/
├── .github/workflows/
│   ├── pr-review.yml           # Push-triggered code review workflow
│   └── scheduled-review.yml    # Scheduled multi-repository scan workflow
├── scripts/
│   ├── ai_code_review.py      # Main review script (830+ lines)
│   └── test_config.py         # Configuration validation test script
├── config.json                # System configuration file
├── CONFIG.md                  # Detailed configuration documentation
├── README-TW.md              # Traditional Chinese documentation
└── README.md                 # English documentation (this project)
```

## ⚙️ Configuration Guide

### Main Configuration File (`config.json`)

```json
{
  "model": {
    "name": "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "fallback_models": [
      "Llama-3.3-Nemotron-Super-49B-v1",
      "Llama-3.3-70B-Instruct-MI210",
      "Llama-3.3-70B-Instruct-Gaudi3"
    ],
    "max_tokens": 32768,
    "temperature": 0.2,
    "timeout": 90
  },
  "projects": {
    "enabled_repos": [
      "owner/repo1",
      "owner/repo2"
    ],
    "default_repo": "owner/main-repo"
  },
  "review": {
    "max_diff_size": 150000,
    "large_diff_threshold": 300000,
    "chunk_max_tokens": 8192,
    "max_files_detail": 8,
    "overview_max_tokens": 12288,
    "response_language": "en"
  },
  "filters": {
    "ignored_extensions": [".md", ".txt", ".yml", ".yaml", ".json", ".lock", ".png", ".jpg", ".gif", ".svg"],
    "ignored_paths": ["docs/", "documentation/", ".github/", "node_modules/", "dist/", "build/", ".vscode/"],
    "code_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".cs", ".swift", ".kt"]
  },
  "prompts": {
    "include_line_numbers": true,
    "detailed_analysis": true,
    "security_focus": true,
    "performance_analysis": true
  }
}
```

For detailed configuration instructions, see [CONFIG.md](CONFIG.md)

### Severity Classification
- **CRITICAL**: Security vulnerabilities, data loss risks, system failures
- **MAJOR**: Performance issues, design flaws, breaking changes
- **MINOR**: Code style, optimization opportunities, suggestions

## 🚀 Quick Start

### 1. Prerequisites

#### Prepare LLM Service
Supports any service compatible with OpenAI API format:
- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic**: Claude series
- **Open Source Solutions**: Ollama, vLLM, Text Generation Inference
- **Other Providers**: Any service supporting OpenAI API format

#### Supported Programming Languages
Full support: Python, JavaScript, TypeScript, Java, C++, C, Go, Rust, PHP, Ruby, C#, Swift, Kotlin

### 2. Configure GitHub Secrets

Since this system requires **cross-repository operations** (accessing other repositories from the PR-Agent repository), you must use a Personal Access Token.

Go to repository `Settings > Secrets and variables > Actions` and add:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `GH_TOKEN` | GitHub Personal Access Token | `ghp_xxxxx...` |
| `OPENAI_KEY` | LLM Service API Key | `sk-xxxxx...` |
| `OPENAI_BASE_URL` | LLM Service Base URL | `https://api.xxx.com/v1` |

> **Important Notes**:
> - The above 3 Secrets need to be **manually configured**
> - `GITHUB_SHA`, `GITHUB_REPOSITORY` etc. are **built-in environment variables automatically provided** by GitHub Actions
> - You neither need nor can manually configure these built-in variables

#### Creating a Personal Access Token

1. Go to [GitHub Settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token"** > **"Generate new token (classic)"**
3. Configure Token Information:
   - **Note**: `AI Code Review Token`
   - **Expiration**: Recommend 90 days (adjust as needed)
   - **Select scopes**: Check the following permissions
     - ✅ `repo` - Full repository permissions (including private repositories)
     - ✅ `write:discussion` - Discussion write permissions (optional)

4. Click **"Generate token"**
5. **Important**: Immediately copy the token and save it to a secure location

> **Permission Explanation**:
> - `repo` permission includes the ability to create issues
> - Supports cross-repository operations, can create review issues in any repository in the enabled_repos list

> **Security Reminder**:
> - Token has full repository permissions for your account, please keep it secure
> - Update token regularly (recommend every 90 days)
> - If token is compromised, immediately revoke it in GitHub settings

### 3. Configure Project Settings

#### Basic Configuration
```json
{
  "model": {
    "name": "your-model-name"
  },
  "projects": {
    "enabled_repos": ["owner/repo-name"],
    "default_repo": "owner/repo-name"
  },
  "review": {
    "response_language": "en"
  }
}
```

#### Multi-Project Configuration
```json
{
  "projects": {
    "enabled_repos": [
      "org/project1",
      "org/project2",
      "user/personal-project"
    ],
    "default_repo": "org/project1"
  }
}
```

#### Global Enable
```json
{
  "projects": {
    "enabled_repos": ["*"]
  }
}
```

### 4. Configuration Validation

Before running the main script, you can first run configuration validation:

```bash
python scripts/test_config.py
```

Successful output example:
```
🔍 Testing configuration file...
✅ Configuration validation passed
   Model: Llama-4-Maverick-17B-128E-Instruct-FP8
   Language: en
   Enabled repos: 4 repositories
   Max tokens: 32,768
   Temperature: 0.2
🎉 Configuration test completed successfully!
```

### 5. Test Run

Submit changes to trigger automatic review:

```bash
git add .
git commit -m "Add AI code review configuration"
git push origin main
```

Go to the `Actions` page to view execution results.

## 📋 Workflow Documentation

### 🔄 Push Trigger Mode (pr-review.yml)

**Trigger Conditions**:
- ✅ Push to any branch
- ✅ Manual trigger (workflow_dispatch)
- ❌ Skip when modifying documentation files (`.md`, `.gitignore`, `LICENSE`, `docs/**`)

**Workflow Process**:
1. **Environment Setup** → Checkout code, setup Python 3.11, install dependencies
2. **Configuration Validation** → Run `test_config.py` to validate configuration file
3. **Code Review** → Execute main review script
4. **Publish Results** → Create Issue in target repository to publish review results

### 🕐 Scheduled Scan Mode (scheduled-review.yml)

**Execution Time**:
- **Scheduled Trigger**: Daily at 2:00 AM UTC+8 (6:00 PM UTC)
- **Manual Trigger**: Can customize scan time range, maximum commits per repository, and concurrency

**Scan Logic**:
1. **Repository Traversal** → Scan all repositories in `enabled_repos`
2. **Time Filtering** → Only process commits from the last 24 hours (adjustable)
3. **Duplicate Check** → Automatically skip commits that already have review Issues
4. **Parallel Processing** → Simultaneously process multiple repositories and commits
5. **Quantity Limit** → Process up to 3 latest commits per repository (adjustable)
6. **Concurrency Limit** → Set `SCAN_CONCURRENCY` to control parallel repository scans (default: 4)

### Review Processing Flow

1. **Project Check** → Confirm project is in allow list
2. **Token Permission Test** → Verify GitHub Token permissions and type
3. **Commit Analysis** → Get change content and statistics
4. **Smart Filtering** → Skip documentation changes, merge commits
5. **Strategy Selection** → Choose review method based on change size:
   - **Small Changes** (< 150KB): Full analysis
   - **Large Changes** (> 300KB): Segmented processing, focus on top 8 files with most changes
6. **AI Analysis** → Execute comprehensive code review
7. **Publish Results** → Create review Issue in target repository

### Large Change Processing Mechanism
- **Threshold Detection**: Trigger segmented mode when exceeding 300KB characters
- **Focus Review**: Priority processing of 8 files with the most changes
- **Parallel Processing**: Simultaneously process multiple file segments for improved efficiency
- **Consolidated Report**: Generate overall overview and specific recommendations

## 🔧 Advanced Configuration

### Model Configuration Optimization
```json
{
  "model": {
    "name": "primary-model",
    "fallback_models": ["backup-model-1", "backup-model-2"],
    "max_tokens": 32768,
    "temperature": 0.1,
    "timeout": 120
  }
}
```

### Custom Filter Rules
```json
{
  "filters": {
    "ignored_extensions": [".md", ".txt", ".png", ".jpg"],
    "ignored_paths": ["docs/", "dist/", ".vscode/", "tests/fixtures/"],
    "code_extensions": [".py", ".js", ".ts", ".java", ".go"]
  }
}
```

### Review Strategy Adjustment
```json
{
  "review": {
    "max_diff_size": 200000,
    "large_diff_threshold": 500000,
    "chunk_max_tokens": 10240,
    "max_files_detail": 10,
    "overview_max_tokens": 16384
  }
}
```

### Prompt Configuration
```json
{
  "prompts": {
    "include_line_numbers": true,
    "detailed_analysis": true,
    "security_focus": true,
    "performance_analysis": true
  }
}
```

## 📊 Review Report Example

### Standard Report Format (GitHub Issue)
```markdown
🤖 AI Code Review - Commit abc12345

## AI Code Review Report

**Review Time**: 2024-01-20 14:30:25 UTC+8
**Commit**: [abc12345](https://github.com/owner/repo/commit/abc12345)
**Author**: John Doe
**Message**: Implement user authentication system
**Model**: Llama-4-Maverick-17B-128E-Instruct-FP8
**Change Statistics**: 15 files, +342 lines, -89 lines

---

## 🔒 Security Analysis

### CRITICAL Issues
- **SQL Injection Risk** (user_service.py:42)
  - Direct string concatenation to build SQL queries
  - Recommendation: Use parameterized queries or ORM

### MAJOR Issues
- **Hardcoded API Key** (config.py:15)
  - Sensitive information should not be hardcoded in source code
  - Recommendation: Use environment variables or secure configuration management

## ⚡ Performance Analysis

### MAJOR Issues
- **N+1 Query Problem** (user_repository.py:78)
  - Executing database queries in a loop
  - Recommendation: Use batch queries or lazy loading

### MINOR Optimizations
- **Connection Pool Configuration** (database.py:25)
  - Consider configuring connection pool for improved performance
  - Recommendation: Set appropriate maximum connection count

## 📝 Code Quality

### POSITIVE Strengths
- ✅ Good error handling implementation
- ✅ Clear function naming and comments
- ✅ Appropriate unit test coverage

### MINOR Suggestions
- **Variable Naming** (auth_controller.py:156)
  - `tmp_var` could use a more descriptive name
  - Recommendation: `temporary_session_data`

## 🧪 Testing Suggestions

- Add boundary condition tests (null values, extreme values)
- Consider adding integration tests covering authentication flow
- Recommend testing exception handling logic

## 📋 Summary and Recommendations

### Priority Actions (High Risk)
1. Fix SQL injection vulnerability
2. Remove hardcoded API keys
3. Resolve N+1 query performance issue

### Follow-up Optimizations (Medium Risk)
- Improve variable naming conventions
- Add more test cases
- Consider performance optimization strategies

---

### 📋 Review Notes
- This review is automatically generated by AI, please combine with human judgment
- Recommend prioritizing CRITICAL and MAJOR issues by severity
- If you have questions or need further discussion, please comment below this issue

### 🔗 Related Links
- [View Commit Changes](https://github.com/owner/repo/commit/abc12345)
- [View File Diff](https://github.com/owner/repo/commit/abc12345.diff)
- [Project Configuration](https://github.com/owner/repo/blob/main/config.json)

---
*Generated by [PR-Agent](https://github.com/sheng1111/AI-Code-Review-Agent)*
```

**Review Report Features**:
- 📌 **Structured Analysis**: Categorized by security, performance, quality
- 💬 **Team Discussion Support**: Issue format facilitates collaborative communication
- 🏷️ **Automatic Label Classification**: `ai-code-review`, `automated` labels
- 🔍 **Searchable and Filterable**: Easy historical tracking and management
- ✅ **Track Resolution Status**: Can mark issues as resolved
- 📊 **Detailed Statistics**: Includes change statistics and file information

## 💡 Best Practices

### Model Selection Recommendations
- **High Accuracy Requirements**: Use GPT-4 or Claude-3
- **Cost Considerations**: Use open-source models like Llama series
- **Chinese Optimization**: Choose models with better Chinese support
- **Reliability Considerations**: Configure multiple fallback models to ensure service availability

### Performance Optimization Tips
1. **Appropriate max_tokens**: Adjust based on model capabilities (recommend 16K-32K)
2. **Reasonable temperature setting**: 0.1-0.3 suitable for code review
3. **Concurrency control**: Avoid exceeding API rate limits
4. **Project scope control**: Only enable automatic review for important projects
5. **Adjust `SCAN_CONCURRENCY`**: Increase thread count to reduce scheduled scan time

### Cost Control Strategies
1. **Set appropriate file size limits** (recommend full analysis within 150KB)
2. **Filter non-critical file types** (exclude images, documents, configuration files)
3. **Use lower-cost models** (open-source models or smaller parameter models)
4. **Limit concurrent file processing** (focus analysis on 8 files for large changes)
5. **Adjust scheduled scan frequency** (default daily, adjust based on needs)

### Multi-Repository Management Tips
1. **Group Management**: Categorize related projects for batch configuration
2. **Priority Setting**: Important projects can be set for more frequent scanning
3. **Permission Management**: Ensure PAT has appropriate permissions for all target repositories
4. **Monitoring and Alerts**: Regularly check review execution status and error logs

## ❓ Frequently Asked Questions

### Q: Why don't I see review results?
**Checklist**:
- [ ] GitHub Secrets configured correctly (`GH_TOKEN`, `OPENAI_KEY`, `OPENAI_BASE_URL`)
- [ ] Token has sufficient permissions (needs `repo` permission to create issues)
- [ ] LLM service responding normally
- [ ] Project is in `enabled_repos` list
- [ ] Check Actions execution logs for errors
- [ ] Check target repository Issues page for `ai-code-review` labeled issues
- [ ] Confirm changes are not in filter list (non-documentation files)

### Q: How to handle 403 permission errors?
**Common Causes and Solutions**:
- **Fine-grained PAT cross-repository limitations**: Switch to Classic Personal Access Token
- **Insufficient token permissions**: Ensure includes `repo` permission (not just `public_repo`)
- **Token expired**: Check and update expired PAT
- **Organization setting restrictions**: Check organization's Token policy settings
- **Repository doesn't exist or no permission**: Confirm repository name is correct and PAT owner has permissions

### Q: How to reduce review costs?
**Effective Strategies**:
- **Adjust Token Limits**: Lower `max_tokens`, `chunk_max_tokens`
- **Filter More Files**: Expand `ignored_extensions` and `ignored_paths`
- **Use Cheaper Models**: Choose lower-cost LLM services
- **Limit Processing Scope**: Reduce `max_files_detail` count
- **Adjust Scan Frequency**: Lower scheduled scan frequency (e.g., weekly)
- **Set Size Limits**: Lower `max_diff_size` to skip very large changes

### Q: What programming languages are supported?
**Complete Support List**:
- **Mainstream Languages**: Python, JavaScript, TypeScript, Java, C++, C
- **Emerging Languages**: Go, Rust, Swift, Kotlin
- **Scripting Languages**: PHP, Ruby, Shell
- **Enterprise Languages**: C#, VB.NET
- **Configuration Languages**: YAML, JSON (adjustable via `code_extensions`)

### Q: How to customize review focus?
**Prompt Configuration Adjustment**:
```json
{
  "prompts": {
    "include_line_numbers": true,    // Include line number information
    "detailed_analysis": false,      // Simplify analysis to reduce costs
    "security_focus": true,          // Strengthen security checks
    "performance_analysis": false    // Disable performance analysis for speed
  }
}
```

### Q: What if scheduled scans don't execute?
**Check Items**:
- **Workflow Enabled**: Confirm `scheduled-review.yml` is enabled
- **Timezone Settings**: Confirm cron expression matches expected time
- **Repository Activity**: GitHub may pause scheduled tasks for inactive repositories
- **Manual Testing**: Use workflow_dispatch to manually trigger tests
- **Permission Check**: Confirm Actions has execution permissions

## 🆘 Troubleshooting

### 1. Cross-Repository Access Issues

**Problem Symptoms**:
```
Error: HttpError: Not Found
or
Error: 403 Forbidden
```

**Diagnostic Steps**:
```bash
# Test Token basic permissions
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/user

# Test specific repository permissions
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/USERNAME/REPO_NAME

# Test Issues creation permissions
curl -X POST \
     -H "Authorization: token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.github.com/repos/USERNAME/REPO_NAME/issues \
     -d '{"title":"Test Issue","body":"Test"}'
```

**Solutions**:
1. **Use Classic PAT**: Avoid Fine-grained PAT cross-repository limitations
2. **Ensure repo permissions**: Must include full `repo` permission
3. **Check repository settings**: Confirm target repository allows Issues feature

### 2. LLM API Connection Issues

**Common Errors**:
```
Error: Connection timeout
or
Error: Invalid API key
```

**Test API Connection**:
```bash
curl -X POST YOUR_BASE_URL/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

**Solutions**:
1. **Check Network Connection**: Ensure server can connect to LLM service
2. **Verify API Key**: Confirm key is valid and not expired
3. **Check Model Name**: Confirm model name matches what provider offers
4. **Adjust Timeout**: Increase timeout setting value

### 3. Configuration File Validation

**Validate Configuration Syntax**:
```bash
# Check JSON syntax
python -c "import json; print('✅ Valid JSON' if json.load(open('config.json')) else '❌ Invalid JSON')"

# Run full configuration test
python scripts/test_config.py
```

**Common Configuration Errors**:
- JSON syntax errors (missing commas, quotes)
- Missing required fields
- Values outside limits (e.g., temperature > 2.0)
- Incorrect repository name format

### 4. Large File Processing Issues

**Problem Symptoms**: Timeout or out of memory

**Solution Strategies**:
```json
{
  "review": {
    "max_diff_size": 100000,        // Lower single processing size
    "large_diff_threshold": 200000, // Lower segmentation threshold
    "chunk_max_tokens": 4096,       // Reduce tokens per segment
    "max_files_detail": 5           // Reduce detailed analysis file count
  }
}
```

### 5. GitHub Actions Permission Settings

**Repository Permission Settings**:
1. Go to `Settings > Actions > General`
2. Set **Workflow permissions** to **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**

**Organization Level Permissions**:
- Confirm organization allows Personal Access Token
- Check organization's Actions usage policies

## 📈 Monitoring and Maintenance

### Key Performance Indicators
- **Processing Time**: Average time per review
- **Token Usage**: API call cost statistics
- **Success Rate**: Review completion percentage
- **Error Rate**: Failed request classification statistics
- **Coverage Rate**: Reviewed commits vs total commits ratio

### Log Analysis Example
View GitHub Actions execution logs:
```
🔍 Testing configuration file...
✅ Configuration validation passed
   Model: Llama-4-Maverick-17B-128E-Instruct-FP8
   Language: en
   Enabled repos: 4 repositories
   Max tokens: 32,768
   Temperature: 0.2

Testing GitHub Token permissions...
Token is valid, user: sheng1111
Token type: Classic
Classic PAT scopes: ['repo', 'workflow']
SUCCESS: Token has 'repo' permission for cross-repository operations

Configuration Summary:
  Model: Llama-4-Maverick-17B-128E-Instruct-FP8
  Fallback Models: 3 configured
  Max Tokens: 32,768
  Temperature: 0.2
  Large Diff Threshold: 300,000 chars
  Response Language: en
  Enabled Repositories: 4

Review statistics: 5 files changed
Change size: 12,450 chars, using full analysis
AI code review completed successfully
Review issue created: https://github.com/owner/repo/issues/123
```

### Regular Maintenance Checklist
- [ ] **Monthly**: Check PAT expiration time, update in advance
- [ ] **Quarterly**: Review LLM service costs and usage
- [ ] **Quarterly**: Update configuration to adapt to new project needs
- [ ] **Semi-annually**: Evaluate model performance, consider upgrades
- [ ] **Semi-annually**: Clean up expired review Issues

### Cost Optimization Recommendations
1. **Monitor API Usage**: Set usage alerts
2. **Adjust Scan Strategy**: High frequency for important projects, low frequency for general projects
3. **Optimize Filter Rules**: Continuously improve ignore lists
4. **Choose Appropriate Models**: Balance cost and quality

## 📄 License and Acknowledgments

### Open Source License
This project is open-sourced under the **MIT License**, and community contributions and improvements are welcome.

### Technology Stack Acknowledgments
- **Python 3.11+**: Primary development language
- **GitHub Actions**: CI/CD automation platform
- **OpenAI API Compatible Format**: LLM service interface standard
- **Requests Library**: HTTP request handling

### Contribution Guidelines
Welcome to submit Issues and Pull Requests:
1. **Bug Reports**: Describe detailed steps to reproduce the issue
2. **Feature Suggestions**: Explain use cases and expected effects
3. **Code Contributions**: Follow existing code style
4. **Documentation Improvements**: Help improve usage instructions

---

**Project Maintainer**: [@sheng1111](https://github.com/sheng1111)
**Last Updated**: JUNE 2025
**Version**: v1.0 