#!/usr/bin/env python3
"""
Configuration Validation Test Script
Validates config.json structure and values before running the main AI code review script.
"""

import json
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "model": {
        "name": "gpt-5.6-luna",
        "fallback_models": [],
        "api_mode": "responses",
        "reasoning_effort": "low",
        "verbosity": "low",
        "service_tier": "flex",
        "flex_fallback_to_auto": True,
        "max_retries": 3,
        "retry_backoff_seconds": 1.0,
        "max_tokens": 16384,
        "temperature": None,
        "timeout": 900
    },
    "projects": {
        "enabled_repos": ["*"]
    },
    "review": {
        "max_diff_size": 150000,
        "large_diff_threshold": 150000,
        "chunk_max_tokens": 8192,
        "chunk_concurrency": 2,
        "response_language": "zh-TW"
    },
    "filters": {
        "ignored_extensions": [".md", ".txt", ".lock", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"],
        "ignored_paths": ["docs/", "documentation/", "node_modules/", "dist/", "build/", ".vscode/"],
        "code_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".cs", ".swift", ".kt"]
    },
    "prompts": {
        "include_line_numbers": True,
        "detailed_analysis": True,
        "security_focus": True,
        "performance_analysis": True
    }
}

_BCP47_RE = re.compile(
    r"^(?:"
    r"(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}|[A-Za-z]{4}|[A-Za-z]{5,8})"
    r"(?:-[A-Za-z]{4})?"
    r"(?:-(?:[A-Za-z]{2}|[0-9]{3}))?"
    r"(?:-(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*"
    r"(?:-[0-9A-WY-Za-wy-z](?:-[A-Za-z0-9]{2,8})+)*"
    r"(?:-x(?:-[A-Za-z0-9]{1,8})+)?"
    r"|x(?:-[A-Za-z0-9]{1,8})+"
    r")$"
)
_BCP47_GRANDFATHERED = {
    "art-lojban", "cel-gaulish", "en-gb-oed", "i-ami", "i-bnn", "i-default",
    "i-enochian", "i-hak", "i-klingon", "i-lux", "i-mingo", "i-navajo",
    "i-pwn", "i-tao", "i-tay", "i-tsu", "no-bok", "no-nyn", "sgn-be-fr",
    "sgn-be-nl", "sgn-ch-de", "zh-guoyu", "zh-hakka", "zh-min", "zh-min-nan",
    "zh-xiang",
}


def is_valid_bcp47(language_tag):
    """Return whether a value is a safe, structurally valid BCP 47 language tag."""
    if not isinstance(language_tag, str):
        return False
    normalized = language_tag.strip()
    return normalized.lower() in _BCP47_GRANDFATHERED or bool(_BCP47_RE.fullmatch(normalized))


def merge_config(defaults, overrides):
    """Recursively merge user config over defaults."""
    merged = defaults.copy()
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def validate_config_structure(config):
    """Validate configuration structure and required fields"""
    required_structure = {
        "model": {
            "name": str,
            "fallback_models": list,
            "api_mode": str,
            "reasoning_effort": str,
            "verbosity": str,
            "service_tier": (str, type(None)),
            "flex_fallback_to_auto": bool,
            "max_retries": int,
            "retry_backoff_seconds": (int, float),
            "max_tokens": int,
            "temperature": (int, float, type(None)),
            "timeout": int
        },
        "projects": {
            "enabled_repos": list
        },
        "review": {
            "max_diff_size": int,
            "large_diff_threshold": int,
            "chunk_max_tokens": int,
            "chunk_concurrency": int,
            "response_language": str
        },
        "filters": {
            "ignored_extensions": list,
            "ignored_paths": list,
            "code_extensions": list
        },
        "prompts": {
            "include_line_numbers": bool,
            "detailed_analysis": bool,
            "security_focus": bool,
            "performance_analysis": bool
        }
    }
    
    def validate_section(section_name, section_config, expected_structure):
        """Validate a configuration section"""
        if section_name not in section_config:
            raise ValueError(f"Missing required section: {section_name}")
        
        section_data = section_config[section_name]
        if not isinstance(section_data, dict):
            raise ValueError(f"Section '{section_name}' must be an object")
        
        for field_name, field_type in expected_structure.items():
            if field_name not in section_data:
                raise ValueError(f"Missing required field: {section_name}.{field_name}")
            
            field_value = section_data[field_name]
            if isinstance(field_type, tuple):
                # Multiple allowed types
                if not isinstance(field_value, field_type):
                    type_names = " or ".join(t.__name__ for t in field_type)
                    raise ValueError(f"Field '{section_name}.{field_name}' must be {type_names}, got {type(field_value).__name__}")
            else:
                # Single type
                if not isinstance(field_value, field_type):
                    raise ValueError(f"Field '{section_name}.{field_name}' must be {field_type.__name__}, got {type(field_value).__name__}")
    
    # Validate each section
    for section_name, section_structure in required_structure.items():
        validate_section(section_name, config, section_structure)
    
    # Additional value validations
    model_config = config["model"]
    if not model_config["name"].strip():
        raise ValueError("model.name cannot be empty")
    if model_config["name"] in model_config["fallback_models"]:
        raise ValueError("model.fallback_models cannot contain model.name")
    if not all(isinstance(model, str) and model.strip() for model in model_config["fallback_models"]):
        raise ValueError("All items in model.fallback_models must be non-empty strings")
    if model_config["api_mode"] not in ["responses", "chat_completions"]:
        raise ValueError("model.api_mode must be 'responses' or 'chat_completions'")
    if model_config["reasoning_effort"] not in ["none", "minimal", "low", "medium", "high", "xhigh", "max"]:
        raise ValueError("model.reasoning_effort must be one of: none, minimal, low, medium, high, xhigh, max")
    if model_config["verbosity"] not in ["low", "medium", "high"]:
        raise ValueError("model.verbosity must be one of: low, medium, high")
    if model_config["service_tier"] not in [None, "auto", "default", "flex"]:
        raise ValueError("model.service_tier must be one of: auto, default, flex")
    if model_config["max_retries"] <= 0 or model_config["max_retries"] > 10:
        raise ValueError("model.max_retries must be between 1 and 10")
    if model_config["retry_backoff_seconds"] < 0 or model_config["retry_backoff_seconds"] > 60:
        raise ValueError("model.retry_backoff_seconds must be between 0 and 60")
    if model_config["max_tokens"] <= 0:
        raise ValueError("model.max_tokens must be positive")
    if model_config["temperature"] is not None and not (0.0 <= model_config["temperature"] <= 2.0):
        raise ValueError("model.temperature must be between 0.0 and 2.0")
    if model_config["timeout"] <= 0:
        raise ValueError("model.timeout must be positive")
    
    review_config = config["review"]
    if review_config["max_diff_size"] <= 0:
        raise ValueError("review.max_diff_size must be positive")
    if review_config["large_diff_threshold"] <= 0:
        raise ValueError("review.large_diff_threshold must be positive")
    if review_config["chunk_max_tokens"] <= 0:
        raise ValueError("review.chunk_max_tokens must be positive")
    if review_config["chunk_concurrency"] <= 0 or review_config["chunk_concurrency"] > 16:
        raise ValueError("review.chunk_concurrency must be between 1 and 16")
    if not is_valid_bcp47(review_config["response_language"]):
        raise ValueError("review.response_language must be a valid BCP 47 language tag")
    
    # Validate enabled_repos format
    projects_config = config["projects"]
    if not projects_config["enabled_repos"]:
        raise ValueError("projects.enabled_repos cannot be empty")
    
    for repo in projects_config["enabled_repos"]:
        if not isinstance(repo, str):
            raise ValueError("All items in projects.enabled_repos must be strings")
        if repo != "*" and "/" not in repo:
            raise ValueError(f"Repository '{repo}' must be in 'owner/repo' format or '*' for all repos")
    
    # Validate file extensions format
    filters_config = config["filters"]
    for ext in filters_config["ignored_extensions"]:
        if not isinstance(ext, str) or not ext.startswith("."):
            raise ValueError(f"File extension '{ext}' must start with '.'")
    
    for ext in filters_config["code_extensions"]:
        if not isinstance(ext, str) or not ext.startswith("."):
            raise ValueError(f"File extension '{ext}' must start with '.'")
    
    return True

def test_config():
    """Test configuration file"""
    config_path = Path(__file__).parent.parent / "config.json"
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            config = merge_config(DEFAULT_CONFIG, user_config)
        else:
            config = DEFAULT_CONFIG
            print("ℹ️  config.json not found; built-in defaults will be used")
            
        # Validate configuration structure
        validate_config_structure(config)
        
        print("✅ Configuration validation passed")
        print(f"   Model: {config['model']['name']}")
        print(f"   Service tier: {config['model']['service_tier']}")
        print(f"   Language: {config['review']['response_language']}")
        repos = config['projects']['enabled_repos']
        repo_summary = "all accessible repositories" if "*" in repos else f"{len(repos)} repositories"
        print(f"   Enabled repos: {repo_summary}")
        print(f"   Max tokens: {config['model']['max_tokens']:,}")
        if config['model']['temperature'] is not None:
            print(f"   Temperature: {config['model']['temperature']}")
        return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except ValueError as e:
        print(f"❌ Configuration validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Testing configuration file...")
    
    if test_config():
        print("🎉 Configuration test completed successfully!")
        sys.exit(0)
    else:
        print("💥 Configuration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
