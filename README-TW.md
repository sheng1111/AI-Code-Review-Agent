# 🤖 AI 程式碼審查系統

GitHub Actions 自動 Code Review 工具，版本 1.0.0。預設使用 OpenAI `gpt-5.6-luna`、low reasoning effort、Flex Processing 與精簡輸出格式，只回報有 diff 證據、可直接交給 AI coding agent 修的問題。

## 快速開始

1. 把這個專案放進你的 repository。
2. 到 `Settings > Secrets and variables > Actions` 設定：
   - `GH_TOKEN`: GitHub PAT，需要可讀 repo、可建立 issue。
   - `OPENAI_KEY`: OpenAI API key。
3. 開啟 GitHub Actions。
4. Push code，review 結果會建立在 Issues，label 是 `ai-code-review`。

`OPENAI_BASE_URL` 可省略；預設是 `https://api.openai.com/v1`。只有使用自架或相容 OpenAI API provider 時才需要設定。

## 預設行為

- Push 到目前 repo 時，自動 review 該 commit。
- Scheduled workflow 預設掃描 `GH_TOKEN` 可存取的全部 repository。
- 不需要設定 `default_repo`。
- 不需要列 repo；沒指定就是全監控。
- 如果只想掃特定 repo，才設定 `projects.enabled_repos`。
- 無可修問題時，輸出固定為：`未發現需要修改的問題。`

## 最小設定

`config.json` 可以只保留語言：

```json
{
  "review": {
    "response_language": "zh-TW"
  }
}
```

甚至刪掉 `config.json` 也能跑，系統會使用內建預設。

## 內建模型設定

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

`temperature` 不放在預設 config。GPT-5.6 code review 主要用 `reasoning_effort`、`verbosity` 和嚴格 prompt contract 控制輸出。

## Flex Processing

預設 `service_tier` 是 `flex`，適合 GitHub Actions 這種非同步 review：成本較低，但可能較慢或偶爾資源不足。若 Flex 回傳資源不足，預設會改用 `service_tier: "auto"` 重試；若成本優先，可設 `flex_fallback_to_auto: false`。若要固定使用專案標準路由，可改成：

```json
{
  "model": {
    "service_tier": "auto"
  }
}
```

## 輸出語言

`review.response_language` 預設為 `zh-TW`。支援任何結構有效的 BCP 47 語言標籤，例如 `en-US`、`zh-Hant-TW`、`sr-Latn-RS`、`es-419`；程式碼、識別字、路徑與 severity label 會維持原文。

## 指定 Repo 白名單

只有不想全監控時才需要：

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

## 輸出格式

有問題時，每個 finding 會包含：

- `位置`: 檔案與 line/hunk
- `證據`: 來自 diff 的具體證據
- `影響`: 會造成什麼失敗
- `修法`: 明確修改方向
- `驗證`: 測試或指令
- `AI_AGENT_FIX_PROMPT`: 可直接交給 AI agent 的修復指令

沒有問題時不會硬提問題。

## 本機驗證

```bash
python3 scripts/test_config.py
python3 -m unittest discover -s tests -v
python3 scripts/benchmark_review.py
```

GitHub Actions 已更新為目前的 `actions/checkout@v7` 與 `actions/setup-python@v7`，會升級 pip 並安裝最新相容的 Requests 2.x。可重現的改善前後基準與瓶頸分析請見 [PERFORMANCE.md](PERFORMANCE.md)。

## 進階文件

更多設定見 [CONFIG.md](CONFIG.md)。
