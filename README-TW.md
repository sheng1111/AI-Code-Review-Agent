# 🤖 AI 程式碼審查系統

基於大型語言模型的自動化程式碼審查工具，提供專業、全面的程式碼品質分析。支援多倉庫監控、自動審查和智能分析。

## ✨ 核心功能

### 🔍 多種觸發模式

#### 1. Push 觸發模式（單倉庫）
- **觸發條件**：Push 到任何分支時自動執行
- **智能過濾**：自動跳過文檔變更（`.md`、`.txt`）和 merge commit
- **支援手動觸發**：可指定特定 commit SHA 進行審查

#### 2. 定時掃描模式（多倉庫）
- **定時執行**：每日 UTC+8 凌晨 2:00 自動掃描
- **多倉庫支援**：同時監控配置清單中的所有倉庫
- **智能限制**：每個倉庫最多處理 3 個最新 commits
- **避免重複**：自動跳過已審查的 commits

### 📊 專業分析維度
- **安全性分析**：SQL 注入、XSS、CSRF 漏洞檢測
- **效能評估**：演算法複雜度、資料庫優化、記憶體使用
- **程式碼品質**：可讀性、維護性、SOLID 原則檢查
- **測試覆蓋**：單元測試建議、邊界條件檢查
- **最佳實踐**：語言特定規範、設計模式評估

### 🌍 多語言回應支援
支援 10 種語言的程式碼審查報告：
- 🇹🇼 繁體中文 (`zh-TW`)
- 🇨🇳 簡體中文 (`zh-CN`)
- 🇺🇸 英文 (`en`)
- 🇯🇵 日文 (`ja`)
- 🇰🇷 韓文 (`ko`)
- 🇫🇷 法文 (`fr`)
- 🇩🇪 德文 (`de`)
- 🇪🇸 西班牙文 (`es`)
- 🇵🇹 葡萄牙文 (`pt`)
- 🇷🇺 俄文 (`ru`)

### ⚡ 效能優化特性
- **並行處理**：多文件同時審查，提升處理速度
- **智能分段**：大型變更自動分段處理（超過 300KB 時）
- **配置緩存**：減少重複配置載入
- **API 速率控制**：避免頻率限制
- **後備模型**：支援多個後備 LLM 模型確保服務可靠性

## 📂 專案結構

```
PR-Agent/
├── .github/workflows/
│   ├── pr-review.yml           # Push 觸發的程式碼審查工作流程
│   └── scheduled-review.yml    # 定時掃描多倉庫工作流程
├── scripts/
│   ├── ai_code_review.py      # 主要審查腳本（830+ 行）
│   └── test_config.py         # 配置驗證測試腳本
├── config.json                # 系統配置文件
├── CONFIG.md                  # 詳細配置說明文檔
├── README-TW.md              # 繁體中文說明文檔
└── README.md                 # 英文說明文檔（本項目）
```

## ⚙️ 配置說明

### 主要配置文件 (`config.json`)

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
    "response_language": "zh-TW"
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

詳細配置說明請參考 [CONFIG.md](CONFIG.md)

### 嚴重程度分類
- **CRITICAL**：安全漏洞、資料遺失風險、系統失效
- **MAJOR**：效能問題、設計缺陷、破壞性變更
- **MINOR**：程式碼風格、優化機會、建議事項

## 🚀 快速開始

### 1. 準備工作

#### 準備 LLM 服務
支援任何相容 OpenAI API 格式的服務：
- **OpenAI**：GPT-4, GPT-3.5
- **Anthropic**：Claude 系列
- **開源方案**：Ollama, vLLM, Text Generation Inference
- **其他供應商**：任何支援 OpenAI API 格式的服務

#### 支援的程式語言
完整支援：Python、JavaScript、TypeScript、Java、C++、C、Go、Rust、PHP、Ruby、C#、Swift、Kotlin

### 2. 配置 GitHub Secrets

由於本系統需要**跨倉庫操作**（從 PR-Agent 倉庫訪問其他倉庫），必須使用 Personal Access Token。

前往倉庫 `Settings > Secrets and variables > Actions`，新增：

| Secret 名稱 | 說明 | 範例 |
|------------|------|------|
| `GH_TOKEN` | GitHub Personal Access Token | `ghp_xxxxx...` |
| `OPENAI_KEY` | LLM 服務 API Key | `sk-xxxxx...` |
| `OPENAI_BASE_URL` | LLM 服務 Base URL | `https://api.xxx.com/v1` |

> **重要說明**：
> - 以上 3 個 Secrets 需要**手動設定**
> - `GITHUB_SHA`、`GITHUB_REPOSITORY` 等是 **GitHub Actions 自動提供**的內建環境變數
> - 您無需也無法手動設定這些內建變數

#### 創建 Personal Access Token

1. 前往 [GitHub Settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. 點擊 **"Generate new token"** > **"Generate new token (classic)"**
3. 設定 Token 資訊：
   - **Note**: `AI Code Review Token`
   - **Expiration**: 建議設定 90 天（可根據需要調整）
   - **Select scopes**: 勾選以下權限
     - ✅ `repo` - 完整倉庫權限（包含私人倉庫）
     - ✅ `write:discussion` - 討論寫入權限（可選）

4. 點擊 **"Generate token"**
5. **重要**：立即複製 token 並保存到安全位置

> **權限說明**：
> - `repo` 權限包含創建 issues 的能力
> - 支援跨倉庫操作，可在 enabled_repos 列表中的任何倉庫創建審查 issue

> **安全提醒**：
> - Token 具有您帳戶的完整倉庫權限，請妥善保管
> - 定期更新 token（建議每 90 天）
> - 如果 token 洩露，立即在 GitHub 設定中撤銷

### 3. 設定專案配置

#### 基本設定
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
    "response_language": "zh-TW"
  }
}
```

#### 多專案設定
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

#### 全域啟用
```json
{
  "projects": {
    "enabled_repos": ["*"]
  }
}
```

### 4. 配置驗證

在執行主腳本前，可先執行配置驗證：

```bash
python scripts/test_config.py
```

成功輸出範例：
```
🔍 Testing configuration file...
✅ Configuration validation passed
   Model: Llama-4-Maverick-17B-128E-Instruct-FP8
   Language: zh-TW
   Enabled repos: 4 repositories
   Max tokens: 32,768
   Temperature: 0.2
🎉 Configuration test completed successfully!
```

### 5. 測試運行

提交變更以觸發自動審查：

```bash
git add .
git commit -m "Add AI code review configuration"
git push origin main
```

前往 `Actions` 頁面查看執行結果。

## 📋 工作流程說明

### 🔄 Push 觸發模式（pr-review.yml）

**觸發條件**：
- ✅ Push 到任何分支
- ✅ 手動觸發 (workflow_dispatch)
- ❌ 修改文檔文件時跳過（`.md`、`.gitignore`、`LICENSE`、`docs/**`）

**工作流程**：
1. **環境準備** → 檢出代碼、設置 Python 3.11、安裝依賴
2. **配置驗證** → 執行 `test_config.py` 驗證配置檔案
3. **程式碼審查** → 執行主要審查腳本
4. **結果發布** → 在目標倉庫建立 Issue 發布審查結果

### 🕐 定時掃描模式（scheduled-review.yml）

**執行時間**：
- **定時觸發**：每日 UTC+8 凌晨 2:00（UTC 18:00）
- **手動觸發**：可自訂掃描時間範圍和每倉庫最大 commits 數

**掃描邏輯**：
1. **倉庫遍歷** → 掃描所有 `enabled_repos` 中的倉庫
2. **時間過濾** → 只處理過去 24 小時的 commits（可調整）
3. **重複檢查** → 自動跳過已建立審查 Issue 的 commits
4. **並行處理** → 同時處理多個倉庫和 commits
5. **數量限制** → 每倉庫最多處理 3 個最新 commits（可調整）

### 審查處理流程

1. **專案檢查** → 確認專案在允許清單中
2. **Token 權限測試** → 驗證 GitHub Token 權限和類型
3. **Commit 分析** → 獲取變更內容和統計資訊
4. **智能過濾** → 跳過文檔變更、merge commits
5. **策略選擇** → 根據變更大小選擇審查方式：
   - **小型變更**（< 150KB）：完整分析
   - **大型變更**（> 300KB）：分段處理，重點分析前 8 個最大變更文件
6. **AI 分析** → 執行全面的程式碼審查
7. **結果發布** → 在目標倉庫建立審查 Issue

### 大型變更處理機制
- **閾值檢測**：超過 300KB 字元時觸發分段模式
- **重點審查**：優先處理變更最大的 8 個文件
- **並行處理**：同時處理多個文件片段以提升效率
- **統合報告**：生成整體概覽和具體建議

## 🔧 進階配置

### 模型配置優化
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

### 過濾規則自訂
```json
{
  "filters": {
    "ignored_extensions": [".md", ".txt", ".png", ".jpg"],
    "ignored_paths": ["docs/", "dist/", ".vscode/", "tests/fixtures/"],
    "code_extensions": [".py", ".js", ".ts", ".java", ".go"]
  }
}
```

### 審查策略調整
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

### 提示詞配置
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

## 📊 審查報告範例

### 標準報告格式（GitHub Issue）
```markdown
🤖 AI 程式碼審查 - Commit abc12345

## AI 程式碼審查報告

**審查時間**: 2024-01-20 14:30:25 UTC+8
**Commit**: [abc12345](https://github.com/owner/repo/commit/abc12345)
**作者**: John Doe
**訊息**: Implement user authentication system
**模型**: Llama-4-Maverick-17B-128E-Instruct-FP8
**變更統計**: 15 個文件，+342 行，-89 行

---

## 🔒 安全性分析

### CRITICAL 問題
- **SQL 注入風險** (user_service.py:42)
  - 直接字串拼接構建 SQL 查詢
  - 建議：使用參數化查詢或 ORM

### MAJOR 問題
- **硬編碼 API 金鑰** (config.py:15)
  - 敏感資訊不應硬編碼在原始碼中
  - 建議：使用環境變數或安全配置管理

## ⚡ 效能分析

### MAJOR 問題
- **N+1 查詢問題** (user_repository.py:78)
  - 在迴圈中執行資料庫查詢
  - 建議：使用批次查詢或延遲載入

### MINOR 優化
- **連線池設定** (database.py:25)
  - 考慮配置連線池以提升效能
  - 建議：設定適當的最大連線數

## 📝 程式碼品質

### POSITIVE 優點
- ✅ 良好的錯誤處理實作
- ✅ 清晰的函數命名和註解
- ✅ 適當的單元測試覆蓋

### MINOR 建議
- **變數命名** (auth_controller.py:156)
  - `tmp_var` 可使用更具描述性的名稱
  - 建議：`temporary_session_data`

## 🧪 測試建議

- 新增邊界條件測試（空值、極大值）
- 考慮新增整合測試覆蓋認證流程
- 建議測試異常情況的處理邏輯

## 📋 總結與建議

### 優先處理 (高風險)
1. 修復 SQL 注入漏洞
2. 移除硬編碼的 API 金鑰
3. 解決 N+1 查詢效能問題

### 後續優化 (中風險)
- 改善變數命名規範
- 新增更多測試案例
- 考慮效能優化策略

---

### 📋 審查說明
- 此審查由 AI 自動生成，請結合人工判斷使用
- 建議依照嚴重程度優先處理 CRITICAL 和 MAJOR 問題
- 如有疑問或需要進一步討論，請在此 issue 下方留言

### 🔗 相關連結
- [查看 Commit 變更](https://github.com/owner/repo/commit/abc12345)
- [查看檔案異動](https://github.com/owner/repo/commit/abc12345.diff)
- [專案設定檔](https://github.com/owner/repo/blob/main/config.json)

---
*由 [PR-Agent](https://github.com/sheng1111/AI-Code-Review-Agent) 自動生成*
```

**審查報告特色**：
- 📌 **結構化分析**：按安全性、效能、品質分類
- 💬 **支援團隊討論**：Issue 格式便於協作溝通
- 🏷️ **自動標籤分類**：`ai-code-review`、`automated` 標籤
- 🔍 **可搜尋過濾**：便於歷史追蹤和管理
- ✅ **追蹤解決狀態**：可標記問題為已解決
- 📊 **詳細統計資訊**：包含變更統計和檔案資訊

## 💡 最佳實踐

### 模型選擇建議
- **高精確度需求**：使用 GPT-4 或 Claude-3
- **成本考量**：使用開源模型如 Llama 系列
- **中文優化**：選擇對中文支援較好的模型
- **穩定性考量**：配置多個後備模型確保服務可用性

### 效能優化技巧
1. **適當的 max_tokens**：根據模型能力調整（推薦 16K-32K）
2. **合理的溫度設定**：0.1-0.3 適合程式碼審查
3. **並行度控制**：避免超過 API 速率限制
4. **專案範圍控制**：只對重要專案啟用自動審查

### 成本控制策略
1. **設定合適的文件大小限制**（推薦 150KB 內完整分析）
2. **過濾非關鍵文件類型**（排除圖片、文檔、配置檔案）
3. **使用較低成本的模型**（開源模型或較小參數模型）
4. **限制同時處理的文件數量**（大型變更重點分析 8 個文件）
5. **定時掃描頻率調整**（預設每日一次，可根據需求調整）

### 多倉庫管理技巧
1. **分組管理**：將相關專案歸類，便於批次設定
2. **優先級設定**：重要專案可設定更頻繁的掃描
3. **權限管理**：確保 PAT 對所有目標倉庫都有適當權限
4. **監控告警**：定期檢查審查執行狀態和錯誤日誌

## ❓ 常見問題

### Q: 為什麼沒有看到審查結果？
**檢查項目清單**：
- [ ] GitHub Secrets 設定是否正確（`GH_TOKEN`、`OPENAI_KEY`、`OPENAI_BASE_URL`）
- [ ] Token 權限是否足夠（需要 `repo` 權限以創建 issues）
- [ ] LLM 服務是否正常回應
- [ ] 專案是否在 `enabled_repos` 清單中
- [ ] 查看 Actions 執行日誌是否有錯誤
- [ ] 檢查目標倉庫 Issues 頁面是否有 `ai-code-review` 標籤的 issue
- [ ] 確認變更內容不在過濾清單中（非文檔類文件）

### Q: 遇到 403 權限錯誤怎麼辦？
**常見原因與解決方案**：
- **Fine-grained PAT 跨倉庫限制**：改用 Classic Personal Access Token
- **Token 權限不足**：確保包含 `repo` 權限（不只是 `public_repo`）
- **Token 過期**：檢查並更新過期的 PAT
- **組織設定限制**：檢查組織的 Token 政策設定
- **倉庫不存在或無權限**：確認倉庫名稱正確且 PAT 擁有者有權限

### Q: 如何減少審查成本？
**有效策略**：
- **調整 Token 限制**：降低 `max_tokens`、`chunk_max_tokens`
- **過濾更多文件**：擴充 `ignored_extensions` 和 `ignored_paths`
- **使用較便宜模型**：選擇成本較低的 LLM 服務
- **限制處理範圍**：減少 `max_files_detail` 數量
- **調整掃描頻率**：降低定時掃描頻率（如改為每週）
- **設定大小限制**：降低 `max_diff_size` 跳過特大變更

### Q: 支援哪些程式語言？
**完整支援清單**：
- **主流語言**：Python, JavaScript, TypeScript, Java, C++, C
- **新興語言**：Go, Rust, Swift, Kotlin
- **腳本語言**：PHP, Ruby, Shell
- **企業語言**：C#, VB.NET
- **配置語言**：YAML, JSON（可透過 `code_extensions` 調整）

### Q: 如何自訂審查重點？
**提示詞配置調整**：
```json
{
  "prompts": {
    "include_line_numbers": true,    // 包含行號資訊
    "detailed_analysis": false,      // 簡化分析以降低成本
    "security_focus": true,          // 強化安全性檢查
    "performance_analysis": false    // 關閉效能分析以提升速度
  }
}
```

### Q: 定時掃描沒有執行怎麼辦？
**檢查項目**：
- **工作流程啟用**：確認 `scheduled-review.yml` 已啟用
- **時區設定**：確認 cron 表達式符合預期時間
- **倉庫活動**：GitHub 可能暫停不活躍倉庫的定時任務
- **手動測試**：使用 workflow_dispatch 手動觸發測試
- **權限檢查**：確認 Actions 有執行權限

## 🆘 故障排除

### 1. 跨倉庫訪問問題

**問題現象**：
```
Error: HttpError: Not Found
或
Error: 403 Forbidden
```

**診斷步驟**：
```bash
# 測試 Token 基本權限
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/user

# 測試特定倉庫權限
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/USERNAME/REPO_NAME

# 測試 Issues 建立權限
curl -X POST \
     -H "Authorization: token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.github.com/repos/USERNAME/REPO_NAME/issues \
     -d '{"title":"Test Issue","body":"Test"}'
```

**解決方案**：
1. **使用 Classic PAT**：避免 Fine-grained PAT 的跨倉庫限制
2. **確保 repo 權限**：必須包含完整的 `repo` 權限
3. **檢查倉庫設定**：確認目標倉庫允許 Issues 功能

### 2. LLM API 連接問題

**常見錯誤**：
```
Error: Connection timeout
或
Error: Invalid API key
```

**測試 API 連接**：
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

**解決方案**：
1. **檢查網路連接**：確認伺服器可連接到 LLM 服務
2. **驗證 API 金鑰**：確認金鑰有效且未過期
3. **檢查模型名稱**：確認模型名稱與服務商提供的一致
4. **調整 timeout**：增加 timeout 設定值

### 3. 配置檔案驗證

**驗證配置語法**：
```bash
# 檢查 JSON 語法
python -c "import json; print('✅ Valid JSON' if json.load(open('config.json')) else '❌ Invalid JSON')"

# 執行完整配置測試
python scripts/test_config.py
```

**常見配置錯誤**：
- JSON 語法錯誤（缺少逗號、引號）
- 必要欄位缺失
- 數值範圍超出限制（如 temperature > 2.0）
- 倉庫名稱格式錯誤

### 4. 大型檔案處理問題

**問題現象**：超時或記憶體不足

**解決策略**：
```json
{
  "review": {
    "max_diff_size": 100000,        // 降低單次處理大小
    "large_diff_threshold": 200000, // 降低分段處理閾值
    "chunk_max_tokens": 4096,       // 減少每段 tokens
    "max_files_detail": 5           // 減少詳細分析檔案數
  }
}
```

### 5. GitHub Actions 權限設定

**倉庫權限設定**：
1. 前往 `Settings > Actions > General`
2. **Workflow permissions** 設置為 **"Read and write permissions"**
3. 勾選 **"Allow GitHub Actions to create and approve pull requests"**

**組織層級權限**：
- 確認組織允許 Personal Access Token
- 檢查組織的 Actions 使用政策

## 📈 監控與維護

### 關鍵效能指標
- **處理時間**：單次審查平均耗時
- **Token 使用量**：API 調用成本統計
- **成功率**：審查完成比例
- **錯誤率**：失敗請求分類統計
- **覆蓋率**：已審查 commits 與總 commits 比例

### 日誌分析範例
查看 GitHub Actions 執行日誌：
```
🔍 Testing configuration file...
✅ Configuration validation passed
   Model: Llama-4-Maverick-17B-128E-Instruct-FP8
   Language: zh-TW
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
  Response Language: zh-TW
  Enabled Repositories: 4

Review statistics: 5 files changed
Change size: 12,450 chars, using full analysis
AI code review completed successfully
Review issue created: https://github.com/owner/repo/issues/123
```

### 定期維護檢查清單
- [ ] **每月**：檢查 PAT 到期時間，提前更新
- [ ] **每季**：審查 LLM 服務成本和使用量
- [ ] **每季**：更新配置以適應新專案需求
- [ ] **每半年**：評估模型效能，考慮升級
- [ ] **每半年**：清理過期的審查 Issues

### 成本優化建議
1. **監控 API 使用量**：設定使用量告警
2. **調整掃描策略**：重要專案高頻，一般專案低頻
3. **優化過濾規則**：持續完善忽略清單
4. **選擇合適模型**：平衡成本與品質

## 📄 授權與致謝

### 開源授權
本專案基於 **MIT 授權條款**開源，歡迎社群貢獻和改進。

### 技術棧致謝
- **Python 3.11+**：主要開發語言
- **GitHub Actions**：CI/CD 自動化平台
- **OpenAI API 相容格式**：LLM 服務介面標準
- **Requests 庫**：HTTP 請求處理

### 貢獻指南
歡迎提出 Issues 和 Pull Requests：
1. **Bug 回報**：詳細描述問題重現步驟
2. **功能建議**：說明使用場景和預期效果
3. **程式碼貢獻**：遵循現有程式碼風格
4. **文檔改進**：協助完善使用說明

---

**專案維護者**：[@sheng1111](https://github.com/sheng1111)
**最後更新**：2025年6月
**版本**：v1.0
