#!/usr/bin/env python3
"""
AI Code Review Independent Script
Supports automatic code review with comprehensive analysis including security, performance, quality, etc.
Enhanced with multi-repository monitoring and improved cross-repo permissions handling.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# ========== Load Configuration ==========
@lru_cache(maxsize=1)
def load_config():
    """Load configuration file with caching"""
    config_path = Path(__file__).parent.parent / "config.json"
    
    try:
        if not config_path.exists():
            print(f"Config file not found: {config_path}")
            sys.exit(1)
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print(f"Config loaded: {config_path}")
        return config
            
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)

# Load configuration
CONFIG = load_config()

# ========== Configuration Constants ==========
class ModelConfig:
    """Model configuration constants"""
    MODEL_NAME = CONFIG["model"]["name"]
    FALLBACK_MODELS = CONFIG["model"]["fallback_models"]
    MAX_TOKENS = CONFIG["model"]["max_tokens"]
    TEMPERATURE = CONFIG["model"]["temperature"]
    TIMEOUT = CONFIG["model"]["timeout"]

class ProjectConfig:
    """Project configuration constants"""
    ENABLED_REPOS = CONFIG["projects"]["enabled_repos"]
    DEFAULT_REPO = CONFIG["projects"]["default_repo"]

class ReviewConfig:
    """Review configuration constants"""
    MAX_DIFF_SIZE = CONFIG["review"]["max_diff_size"]
    LARGE_DIFF_THRESHOLD = CONFIG["review"]["large_diff_threshold"]
    CHUNK_MAX_TOKENS = CONFIG["review"]["chunk_max_tokens"]
    MAX_FILES_DETAIL = CONFIG["review"]["max_files_detail"]
    OVERVIEW_MAX_TOKENS = CONFIG["review"]["overview_max_tokens"]
    RESPONSE_LANGUAGE = CONFIG["review"]["response_language"]
    
    IGNORED_EXTENSIONS = CONFIG["filters"]["ignored_extensions"]
    IGNORED_PATHS = CONFIG["filters"]["ignored_paths"]
    CODE_EXTENSIONS = CONFIG["filters"]["code_extensions"]

class PromptConfig:
    """Prompt configuration constants"""
    INCLUDE_LINE_NUMBERS = CONFIG["prompts"]["include_line_numbers"]
    DETAILED_ANALYSIS = CONFIG["prompts"]["detailed_analysis"]
    SECURITY_FOCUS = CONFIG["prompts"]["security_focus"]
    PERFORMANCE_ANALYSIS = CONFIG["prompts"]["performance_analysis"]

def is_repo_enabled(repo_name):
    """Check if project is enabled for code review"""
    enabled_repos = ProjectConfig.ENABLED_REPOS
    
    # Support wildcard "*" to indicate all projects
    if "*" in enabled_repos:
        return True
    
    # Check if it's in the allow list
    return repo_name in enabled_repos

def test_github_token_permissions():
    """Test GitHub token permissions and provide diagnostics"""
    token = os.environ.get('GH_TOKEN')
    if not token:
        print("ERROR: GH_TOKEN environment variable not set")
        return False
        
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("Testing GitHub Token permissions...")
    
    # Test basic user permissions
    try:
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"Token is valid, user: {user_data.get('login')}")
            
            # Check token type
            token_type = "Fine-grained" if token.startswith('github_pat_') else "Classic"
            print(f"Token type: {token_type}")
            
            # Check scopes for classic tokens
            if 'X-OAuth-Scopes' in response.headers:
                scopes = response.headers.get('X-OAuth-Scopes', '').split(', ')
                print(f"Classic PAT scopes: {scopes}")
                
                # Check for essential permissions (repo is required, user is optional for cross-repo operations)
                if 'repo' not in scopes:
                    print(f"ERROR: Missing essential scope: 'repo' - required for cross-repository operations")
                    return False
                else:
                    print(f"SUCCESS: Token has 'repo' permission for cross-repository operations")
                    
                # Check for optional permissions
                if 'user' not in scopes:
                    print(f"INFO: Optional scope 'user' not present - basic user info access will be limited")
                
            else:
                print("INFO: Fine-grained PAT - permissions determined by repository settings")
                
        else:
            print(f"ERROR: Token validation failed: {response.status_code}")
            print(f"Error message: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Token test failed: {str(e)}")
        return False
    
    return True

def get_recent_commits_from_repo(repo_name, hours=None):
    """Get recent commits from a specific repository"""
    token = os.environ['GH_TOKEN']
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Calculate time threshold
    if hours is None:
        hours = int(os.environ.get('SCAN_HOURS', '24'))
    since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
    
    # Get max commits per repo setting
    max_commits = int(os.environ.get('MAX_COMMITS_PER_REPO', '3'))
    
    url = f'https://api.github.com/repos/{repo_name}/commits'
    params = {
        'since': since_time,
        'per_page': max_commits  # Limit to max commits per repo
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            commits = response.json()
            print(f"Repository {repo_name}: Found {len(commits)} recent commits (limit: {max_commits})")
            return commits
        else:
            print(f"WARNING: Cannot get commits from {repo_name}: {response.status_code}")
            if response.status_code == 403:
                print("ERROR: 403 error - Possible permission issue or repository not found")
            return []
    except Exception as e:
        print(f"ERROR: Exception while getting commits from {repo_name}: {str(e)}")
        return []

def scan_all_enabled_repos():
    """Scan all enabled repositories for recent commits"""
    print("Starting scan of all enabled repositories...")
    
    if not test_github_token_permissions():
        print("ERROR: GitHub Token permission test failed, stopping execution")
        return []
    
    repos_to_scan = []
    enabled_repos = ProjectConfig.ENABLED_REPOS
    
    # Handle wildcard case
    if "*" in enabled_repos:
        print("WARNING: Wildcard mode (*) not implemented yet, please specify repositories explicitly in config.json")
        return []
    
    pending_reviews = []
    
    for repo_name in enabled_repos:
        print(f"\nScanning repository: {repo_name}")
        commits = get_recent_commits_from_repo(repo_name)
        
        for commit in commits:
            commit_sha = commit['sha']
            commit_message = commit['commit']['message']
            author = commit['commit']['author']['name']
            commit_date = commit['commit']['author']['date']
            
            print(f"  Commit {commit_sha[:8]}: {commit_message[:50]}...")
            print(f"     Author: {author}, Date: {commit_date}")
            
            # Check if this commit has already been reviewed
            if not has_been_reviewed(repo_name, commit_sha):
                pending_reviews.append({
                    'repo': repo_name,
                    'commit_sha': commit_sha,
                    'commit_message': commit_message,
                    'author': author,
                    'date': commit_date
                })
                print(f"  Added to review queue")
            else:
                print(f"  Already reviewed, skipping")
    
    return pending_reviews

def has_been_reviewed(repo_name, commit_sha):
    """Check if a commit has already been reviewed by looking for existing issues"""
    token = os.environ['GH_TOKEN']
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Search for existing review issues
    search_query = f"repo:{repo_name} is:issue label:ai-code-review \"{commit_sha[:8]}\""
    url = f'https://api.github.com/search/issues'
    params = {'q': search_query}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            results = response.json()
            return results['total_count'] > 0
        else:
            print(f"WARNING: Cannot search existing review issues: {response.status_code}")
            return False
    except Exception as e:
        print(f"WARNING: Error searching review history: {str(e)}")
        return False

def get_commit_diff(commit_sha, repo=None):
    """Get commit diff"""
    token = os.environ['GH_TOKEN']
    repo = repo or os.environ['GITHUB_REPOSITORY']
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3.diff'
    }
    
    url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to get commit diff: {response.status_code}")
        return None

def get_commit_info(commit_sha, repo=None):
    """Get commit information"""
    token = os.environ['GH_TOKEN']
    repo = repo or os.environ['GITHUB_REPOSITORY']
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get commit info: {response.status_code}")
        return None

class LLMAPIError(Exception):
    """Raised when the LLM API call fails"""


def call_llm_api(prompt, max_tokens=None, temperature=None):
    """Unified interface for calling the LLM API

    Raises
    ------
    LLMAPIError
        If the API returns a non-200 status code or the request fails.
    """
    api_key = os.environ['OPENAI_KEY']
    base_url = os.environ['OPENAI_BASE_URL']

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': ModelConfig.MODEL_NAME,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens or ModelConfig.MAX_TOKENS,
        'temperature': temperature or ModelConfig.TEMPERATURE
    }

    try:
        completion_url = f"{base_url.rstrip('/')}/chat/completions"
        response = requests.post(
            completion_url,
            headers=headers,
            json=data,
            timeout=ModelConfig.TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            raise LLMAPIError("LLM response format error")

        # Avoid leaking potential API keys in error responses
        raise LLMAPIError(f"LLM service error {response.status_code}")

    except Exception as e:
        raise LLMAPIError(f"LLM API call failed: {str(e)}") from e

def generate_review_prompt(diff_content, commit_info):
    """Generate code review prompt"""
    max_diff_size = min(len(diff_content), ReviewConfig.MAX_DIFF_SIZE)
    
    # Generate strong language instruction based on configuration
    language_map = {
        "zh-TW": "重要：必須完全使用繁體中文回應，不可使用英文或其他語言。使用專業的程式碼審查術語，格式清晰，提供具體的行號參考。嚴重程度分類：CRITICAL（安全漏洞、系統失效）、MAJOR（效能問題、設計缺陷）、MINOR（程式碼風格、優化建議）。",
        "zh-CN": "重要：必须完全使用简体中文回应，不可使用英文或其他语言。使用专业的代码审查术语，格式清晰，提供具体的行号参考。严重程度分类：CRITICAL（安全漏洞、系统失效）、MAJOR（性能问题、设计缺陷）、MINOR（代码风格、优化建议）。",
        "en": "IMPORTANT: You must respond entirely in English. Use professional code review terminology with clear formatting and specific line number references.",
        "ja": "重要：日本語でのみ回答してください。英語や他の言語を使用しないでください。専門的なコードレビュー用語を使用し、明確な形式と具体的な行番号の参照を提供してください。",
        "ko": "중요: 한국어로만 응답해야 합니다. 영어나 다른 언어를 사용하지 마십시오. 전문적인 코드 리뷰 용어를 사용하고 명확한 형식과 구체적인 행 번호 참조를 제공하십시오.",
        "fr": "IMPORTANT: Vous devez répondre entièrement en français. Utilisez une terminologie professionnelle de révision de code avec un formatage clair et des références de numéros de ligne spécifiques.",
        "de": "WICHTIG: Sie müssen vollständig auf Deutsch antworten. Verwenden Sie professionelle Code-Review-Terminologie mit klarer Formatierung und spezifischen Zeilennummernverweisen.",
        "es": "IMPORTANTE: Debe responder completamente en español. Use terminología profesional de revisión de código con formato claro y referencias específicas de números de línea.",
        "pt": "IMPORTANTE: Você deve responder inteiramente em português. Use terminologia profissional de revisão de código com formatação clara e referências específicas de números de linha.",
        "ru": "ВАЖНО: Вы должны отвечать полностью на русском языке. Используйте профессиональную терминологию обзора кода с четким форматированием и конкретными ссылками на номера строк."
    }
    
    language_instruction = language_map.get(ReviewConfig.RESPONSE_LANGUAGE, language_map["en"])
    
    return f"""You are a senior code reviewer. Please conduct a comprehensive code review of the following Git commit following industry standards.

## Commit Information
- Author: {commit_info.get('commit', {}).get('author', {}).get('name', 'Unknown')}
- Message: {commit_info.get('commit', {}).get('message', 'No message')}
- Timestamp: {commit_info.get('commit', {}).get('author', {}).get('date', 'Unknown')}

## Code Changes
```diff
{diff_content[:max_diff_size]}
```
{f"Note: Due to large changes, only showing first {max_diff_size} characters" if len(diff_content) > max_diff_size else ""}

Please provide a detailed review covering the following aspects:

## Security Analysis
- SQL injection, XSS, CSRF vulnerabilities
- Hardcoded sensitive information (API keys, passwords, secrets)
- Input validation and data sanitization
- Authentication and authorization mechanisms
- Dependency vulnerabilities

## Performance Review
- Algorithm complexity analysis
- Database query optimization
- Memory usage patterns
- Concurrency and thread safety
- Caching strategies
- Resource management

## Code Quality
- Code readability and maintainability
- Function and class design
- Error handling and exception management
- Code duplication and refactoring opportunities
- Naming conventions and documentation quality
- SOLID principles adherence

## Testing Coverage
- Unit test requirements
- Edge case testing
- Error condition testing
- Integration test needs
- Test quality and maintainability

## Best Practices
- Language-specific best practices
- Design pattern usage
- Dependency management
- Documentation completeness
- Configuration management

## Recommendations
- Specific code improvement suggestions
- Refactoring recommendations with rationale
- Technical debt identification
- Long-term maintenance considerations

Please categorize each finding by severity:
- CRITICAL: Security vulnerabilities, data loss risks, system failures
- MAJOR: Performance issues, design flaws, breaking changes
- MINOR: Code style, optimization opportunities, suggestions

Provide specific line numbers where applicable. If code quality is good, please acknowledge positive aspects as well.

{language_instruction}"""

def review_code_with_llm(diff_content, commit_info):
    """Use LLM for code review"""
    prompt = generate_review_prompt(diff_content, commit_info)
    return call_llm_api(prompt, ModelConfig.MAX_TOKENS)

def review_large_diff_in_chunks(diff_content, commit_info):
    """Review large changes in chunks"""
    # Analyze file change statistics
    files_changed = commit_info.get('files', [])
    total_additions = sum(f.get('additions', 0) for f in files_changed)
    total_deletions = sum(f.get('deletions', 0) for f in files_changed)
    
    # Group diff by files
    file_diffs = []
    current_file = None
    current_diff = []
    
    for line in diff_content.split('\n'):
        if line.startswith('diff --git'):
            if current_file and current_diff:
                file_diffs.append((current_file, '\n'.join(current_diff)))
            current_file = line.split(' b/')[-1] if ' b/' in line else 'unknown'
            current_diff = [line]
        else:
            current_diff.append(line)
    
    if current_file and current_diff:
        file_diffs.append((current_file, '\n'.join(current_diff)))
    
    # Generate language instruction for large diff analysis
    language_map = {
        "zh-TW": "重要：必須完全使用繁體中文回應。",
        "zh-CN": "重要：必须完全使用简体中文回应。",
        "en": "IMPORTANT: You must respond entirely in English.",
        "ja": "重要：日本語でのみ回答してください。",
        "ko": "중요: 한국어로만 응답해야 합니다.",
        "fr": "IMPORTANT: Vous devez répondre entièrement en français.",
        "de": "WICHTIG: Sie müssen vollständig auf Deutsch antworten.",
        "es": "IMPORTANTE: Debe responder completamente en español.",
        "pt": "IMPORTANTE: Você deve responder inteiramente em português.",
        "ru": "ВАЖНО: Вы должны отвечать полностью на русском языке."
    }
    language_instruction = language_map.get(ReviewConfig.RESPONSE_LANGUAGE, language_map["en"])
    
    # Generate overview analysis
    overview_prompt = f"""As a senior code reviewer, please analyze the overall impact of this large commit:

## Commit Information
- Author: {commit_info.get('commit', {}).get('author', {}).get('name', 'Unknown')}
- Message: {commit_info.get('commit', {}).get('message', 'No message')}
- Statistics: {len(files_changed)} files changed, +{total_additions}/-{total_deletions} lines

## Changed Files
{chr(10).join([f"- {f.get('filename', 'unknown')}: +{f.get('additions', 0)}/-{f.get('deletions', 0)}" for f in files_changed[:20]])}
{"..." if len(files_changed) > 20 else ""}

Please provide:
1. **Overall Assessment**: Change type, scope and complexity
2. **Focus Areas**: Files/changes requiring special attention
3. **Risk Analysis**: Potential risks from large-scale changes
4. **Recommendations**: Deployment and testing strategies

Use professional code review terminology and industry standards.

{language_instruction}"""
    
    # Get overview analysis
    overview_analysis = call_llm_api(overview_prompt, ReviewConfig.OVERVIEW_MAX_TOKENS)
    
    # Detailed review for important files
    important_files = sorted(files_changed, 
                           key=lambda f: f.get('additions', 0) + f.get('deletions', 0), 
                           reverse=True)[:ReviewConfig.MAX_FILES_DETAIL]
    
    def review_single_file(file_info):
        """Review a single file with optimized processing"""
        filename = file_info.get('filename', 'unknown')
        # Find corresponding diff
        file_diff = None
        for fname, fdiff in file_diffs:
            if fname == filename:
                file_diff = fdiff[:50000]  # Limit single file size
                break
        
        if file_diff:
            file_prompt = f"""Please review the changes in this file:

## File: {filename}
## Change Statistics: +{file_info.get('additions', 0)}/-{file_info.get('deletions', 0)}

```diff
{file_diff}
```

Focus on:
- Security vulnerabilities and risks
- Performance implications
- Potential bugs and issues
- Code quality and maintainability

Provide concise, professional analysis following industry standards.

{language_instruction}"""
            
            file_review = call_llm_api(file_prompt, ReviewConfig.CHUNK_MAX_TOKENS)
            return f"### {filename}\n{file_review}"
        return None

    # Use parallel processing for file reviews (limited concurrency to avoid API limits)
    detailed_reviews = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_file = {executor.submit(review_single_file, file_info): file_info 
                         for file_info in important_files}
        
        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                detailed_reviews.append(result)
            time.sleep(0.5)  # Rate limiting
    
    # Combine results
    final_review = f"""## Large-Scale Change Analysis

{overview_analysis}

## Detailed File Reviews

{chr(10).join(detailed_reviews)}

## Summary and Recommendations

**Testing Focus**: Priority testing required for {len(important_files)} high-impact files
**Deployment Strategy**: Recommend phased deployment with system monitoring
**Risk Assessment**: {len(files_changed)} files affected, comprehensive regression testing advised

---
*Automated large-scale change analysis - combine with human review*"""
    
    return final_review

def should_skip_review(commit_info):
    """Check if review should be skipped"""
    # Check if it's a merge commit
    if len(commit_info.get('parents', [])) > 1:
        print("Merge commit detected, skipping review")
        return True
    
    # Check file changes
    files = commit_info.get('files', [])
    
    # Check if only ignored files were changed
    for file in files:
        filename = file.get('filename', '')
        
        # Check file extensions
        if any(filename.endswith(ext) for ext in ReviewConfig.IGNORED_EXTENSIONS):
            continue
            
        # Check file paths
        if any(pattern in filename for pattern in ReviewConfig.IGNORED_PATHS):
            continue
            
        # If there are non-ignored files, don't skip review
        return False
    
    print("Only documentation or config files changed, skipping review")
    return True

def create_review_issue(commit_sha, review_content, repo=None):
    """Create a code review issue in the target repository with improved error handling"""
    token = os.environ['GH_TOKEN']
    repo = repo or os.environ['GITHUB_REPOSITORY']
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get commit info for title
    commit_info = get_commit_info(commit_sha, repo)
    commit_message = commit_info.get('commit', {}).get('message', 'No message') if commit_info else 'No message'
    commit_author = commit_info.get('commit', {}).get('author', {}).get('name', 'Unknown') if commit_info else 'Unknown'
    
    # Generate issue title
    issue_title = f"🤖 AI Code Review - Commit {commit_sha[:8]}"
    
    # Format issue content
    issue_body = f"""## AI Code Review Report

**Review Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Commit**: [{commit_sha[:8]}](https://github.com/{repo}/commit/{commit_sha})
**Author**: {commit_author}
**Message**: {commit_message}
**Model**: {ModelConfig.MODEL_NAME}

---

{review_content}

---

### 📋 Review Notes
- This review is automatically generated by AI, please combine with human judgment
- Recommend prioritizing CRITICAL and MAJOR issues by severity
- If you have questions or need further discussion, please comment below this issue

### 🔗 Related Links
- [View Commit Changes](https://github.com/{repo}/commit/{commit_sha})
- [View File Diff](https://github.com/{repo}/commit/{commit_sha}.diff)

---
*This review is automatically generated by [AI Code Review Agent](https://github.com/sheng1111/AI-Code-Review-Agent)*
"""
    
    # Create issue with retry mechanism
    url = f'https://api.github.com/repos/{repo}/issues'
    data = {
        'title': issue_title,
        'body': issue_body,
        'labels': ['ai-code-review', 'automated']
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data.get('html_url')
                issue_number = issue_data.get('number')
                print(f"SUCCESS: Code review issue created: {issue_url}")
                print(f"Issue number: #{issue_number}")
                return True
            elif response.status_code == 403:
                error_data = response.json()
                error_msg = error_data.get('message', 'Unknown error')
                print(f"ERROR: 403 permission error: {error_msg}")
                print(f"Checklist:")
                print(f"   - Does Personal Access Token have 'repo' permission?")
                print(f"   - Can token access {repo} repository?")
                print(f"   - Does repository exist with correct permissions?")
                
                if "fine-grained personal access token" in error_msg.lower():
                    print(f"TIP: Fine-grained PAT may not support cross-repo operations, consider using Classic PAT")
                
                return False
            else:
                print(f"WARNING: Failed to create issue (attempt {attempt + 1}/{max_retries}): {response.status_code}")
                print(f"Response: {response.text}")
                
                if attempt < max_retries - 1:
                    print("Retrying after delay...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
        except Exception as e:
            print(f"ERROR: Exception while creating issue (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
    
    # All retries failed, output to console as fallback
    print("\n" + "="*80)
    print("AI Code Review Report (Console Output)")
    print("="*80)
    print(f"Commit: {commit_sha}")
    print(f"Repository: {repo}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*80)
    print(review_content)
    print("="*80)
    print("WARNING: Unable to create GitHub Issue, report output to Actions log")
    print("="*80 + "\n")
    
    return False

def print_config_summary():
    """Display configuration summary"""
    print("Configuration Summary:")
    print(f"  Model: {ModelConfig.MODEL_NAME}")
    print(f"  Max Tokens: {ModelConfig.MAX_TOKENS:,}")
    print(f"  Temperature: {ModelConfig.TEMPERATURE}")
    print(f"  Large Diff Threshold: {ReviewConfig.LARGE_DIFF_THRESHOLD:,} chars")
    print(f"  Max Detailed Files: {ReviewConfig.MAX_FILES_DETAIL}")
    print(f"  Response Language: {ReviewConfig.RESPONSE_LANGUAGE}")
    print(f"  Enabled Repositories: {ProjectConfig.ENABLED_REPOS}")
    print()

def review_single_commit(commit_data):
    """Review a single commit"""
    repo_name = commit_data['repo']
    commit_sha = commit_data['commit_sha']
    
    print(f"\nStarting review for {repo_name} commit {commit_sha[:8]}")
    
    # Get commit info and diff
    commit_info = get_commit_info(commit_sha, repo_name)
    if not commit_info:
        print(f"ERROR: Cannot get commit info")
        return False
    
    # Check if review should be skipped
    if should_skip_review(commit_info):
        print(f"Skipping review")
        return True
    
    diff_content = get_commit_diff(commit_sha, repo_name)
    if not diff_content:
        print(f"ERROR: Cannot get commit diff content")
        return False
    
    files = commit_info.get('files', [])
    print(f"Review statistics: {len(files)} files changed")
    
    # Choose review strategy based on change size
    try:
        if len(diff_content) > ReviewConfig.LARGE_DIFF_THRESHOLD:
            print(f"Large changes ({len(diff_content):,} chars), using chunked analysis")
            review_result = review_large_diff_in_chunks(diff_content, commit_info)
        else:
            print(f"Change size: {len(diff_content):,} chars, using full analysis")
            review_result = review_code_with_llm(diff_content, commit_info)

        print("AI code review completed")

    except LLMAPIError as e:
        print(f"ERROR: {e}")
        return False
    
    # Create review issue in the target repository
    success = create_review_issue(commit_sha, review_result, repo_name)
    
    if success:
        print(f"SUCCESS: Code review process completed for {repo_name}!")
    else:
        print(f"WARNING: Review completed but failed to create issue for {repo_name}")
    
    return success

def main():
    """Main function for AI code review"""
    print("AI Code Review System Starting")
    
    # Check required environment variables
    required_env_vars = ['GH_TOKEN', 'OPENAI_KEY', 'OPENAI_BASE_URL']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Display configuration summary
    print_config_summary()
    
    # Determine execution mode based on environment variables
    # Check for scheduled scan mode indicators (SCAN_HOURS indicates scheduled scan)
    is_scheduled_scan = bool(os.environ.get('SCAN_HOURS'))
    
    if not is_scheduled_scan and os.environ.get('GITHUB_SHA') and os.environ.get('GITHUB_REPOSITORY'):
        # GitHub Actions triggered mode (push to this project)
        print("GitHub Actions Push-Triggered Mode")
        current_repo = os.environ['GITHUB_REPOSITORY']
        target_commit = os.environ.get('TARGET_COMMIT') or os.environ['GITHUB_SHA']
        
        if not is_repo_enabled(current_repo):
            print(f"WARNING: Repository {current_repo} not enabled for code review, skipping")
            return
        
        # Single commit review
        commit_data = {
            'repo': current_repo,
            'commit_sha': target_commit,
            'commit_message': 'GitHub Actions triggered',
            'author': 'Unknown',
            'date': datetime.now().isoformat()
        }
        
        review_single_commit(commit_data)
        
    else:
        # Scheduled scan mode (for other repositories)
        print("Scheduled Scan Mode")
        current_repo = os.environ.get('GITHUB_REPOSITORY')
        
        # Get all enabled repos and exclude current repo if it exists
        enabled_repos = ProjectConfig.ENABLED_REPOS.copy()
        if current_repo and current_repo in enabled_repos:
            enabled_repos.remove(current_repo)
            print(f"Excluded current repository from scheduled scan: {current_repo}")
        
        if not enabled_repos:
            print("No repositories to scan (current repository excluded from scheduled scan)")
            return
        
        # Temporarily override enabled repos for this scan
        original_enabled_repos = ProjectConfig.ENABLED_REPOS
        ProjectConfig.ENABLED_REPOS = enabled_repos
        
        try:
            pending_reviews = scan_all_enabled_repos()
            
            if not pending_reviews:
                print("SUCCESS: No commits need review in other repositories")
                return
            
            print(f"\nFound {len(pending_reviews)} commits pending review")
            
            # Process each commit
            successful_reviews = 0
            for commit_data in pending_reviews:
                try:
                    if review_single_commit(commit_data):
                        successful_reviews += 1
                    time.sleep(1)  # Rate limiting between reviews
                except Exception as e:
                    print(f"ERROR: Failed to review {commit_data['repo']} commit {commit_data['commit_sha'][:8]}: {str(e)}")
                    continue
            
            print(f"\nScan completed! Successfully reviewed {successful_reviews}/{len(pending_reviews)} commits")
        
        finally:
            # Restore original enabled repos
            ProjectConfig.ENABLED_REPOS = original_enabled_repos

if __name__ == "__main__":
    main() 