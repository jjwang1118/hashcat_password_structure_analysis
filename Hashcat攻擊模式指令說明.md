# Hashcat 攻擊模式指令說明

本文件詳細說明 Hashcat 在本實驗中使用的各種攻擊模式、參數意義及實際範例。

---

## 目錄
1. [基礎參數說明](#基礎參數說明)
2. [Mode 3: Mask Attack (純遮罩攻擊)](#mode-3-mask-attack-純遮罩攻擊)
3. [Mode 0: Dictionary Attack (字典攻擊)](#mode-0-dictionary-attack-字典攻擊)
4. [Mode 6: Hybrid Attack (字典+遮罩)](#mode-6-hybrid-attack-字典遮罩)
5. [Mode 7: Hybrid Attack (遮罩+字典)](#mode-7-hybrid-attack-遮罩字典)
6. [進階參數設定](#進階參數設定)

---

## 基礎參數說明

### 通用參數

| 參數 | 說明 | 範例值 |
|------|------|--------|
| `-m` | Hash 類型模式 | `100` (SHA-1) |
| `-a` | 攻擊模式 | `0` (字典), `3` (遮罩), `6`/`7` (混合) |
| `-d` | 指定使用的設備 | `1` (GPU 1), `1,2` (GPU 1&2) |
| `-w` | 工作負載模式 | `1`-`4` (1=低, 4=Nightmare) |
| `-O` | 啟用優化核心（限制密碼長度≤31，提升速度） | 無需參數 |
| `--force` | 強制執行（忽略警告） | 無需參數 |
| `--status` | 顯示狀態 | 無需參數 |
| `--status-json` | 以 JSON 格式輸出狀態 | 無需參數 |
| `--status-timer` | 狀態更新間隔（秒） | `60` |

### Hash 類型 (-m)

常見 Hash 類型：

| 模式 | Hash 類型 | 說明 |
|------|----------|------|
| 0 | MD5 | 128-bit hash |
| 100 | SHA-1 | 160-bit hash (本實驗使用) |
| 1000 | NTLM | Windows 密碼 hash |
| 1400 | SHA-256 | 256-bit hash |
| 1800 | sha512crypt | Linux shadow 檔案 |
| 3200 | bcrypt | 高安全性 hash |

### 工作負載模式 (-w)

| 模式 | 名稱 | GPU 使用率 | 系統回應 | 適用場景 |
|------|------|-----------|---------|---------|
| 1 | Low | ~50% | 流暢 | 日常使用電腦時 |
| 2 | Default | ~75% | 正常 | 預設值 |
| 3 | High | ~90% | 稍慢 | 專注破解時 |
| 4 | Nightmare | ~100% | 可能卡頓 | 專用破解機（本實驗使用） |

### 優化核心 (-O)

**功能說明**：
- 啟用 Hashcat 的優化演算法，大幅提升破解速度
- 速度提升：通常可達 **1.5-2 倍**（取決於 hash 類型和攻擊模式）

**限制**：
- **密碼長度限制**：最多 31 個字符（純 ASCII）
- 部分複雜 hash 類型不支援
- 某些攻擊模式可能無法使用

---

#### 優化原理深入解析

**核心概念**：`-O` 參數讓 Hashcat 使用「特化版本」的 GPU kernel，透過犧牲通用性來換取極致效能。

##### 1. 核心程式碼優化 (Kernel Code Optimization)

一般模式下，Hashcat 必須支援各種長度的密碼（1-256 字元），這需要：
- 動態迴圈處理任意長度
- 條件分支判斷當前處理位置
- 記憶體動態配置

啟用 `-O` 後，Hashcat 使用**編譯時期固定長度**的 kernel：

```c
// 一般模式（動態長度）
for (int i = 0; i < password_len; i++) {
    state = hash_function(state, password[i]);
}

// 優化模式（固定長度，例如 8 字元）
state = hash_function(state, password[0]);
state = hash_function(state, password[1]);
state = hash_function(state, password[2]);
state = hash_function(state, password[3]);
state = hash_function(state, password[4]);
state = hash_function(state, password[5]);
state = hash_function(state, password[6]);
state = hash_function(state, password[7]);
// 編譯器可完全展開，無分支跳轉
```

**優勢**：
- 消除迴圈開銷（loop overhead）
- 消除條件分支（branch prediction misses）
- 編譯器可進行更激進的最佳化（constant folding、instruction reordering）

---

##### 2. 記憶體存取優化 (Memory Access Optimization)

GPU 效能的關鍵在於記憶體頻寬，`-O` 針對記憶體配置做了特化：

| 項目 | 一般模式 | 優化模式 (-O) |
|------|---------|--------------|
| 密碼緩衝區大小 | 動態（最大 256 bytes） | 固定 32 bytes |
| 記憶體對齊 | 可能未對齊 | 強制 16-byte 對齊 |
| 寄存器使用 | 較少（需處理通用情境） | 最大化（所有變數盡可能存於 registers） |
| Global Memory 存取 | 較頻繁 | 最小化（優先使用 shared memory） |

**為何限制 31 字元**：
- GPU 寄存器通常為 32-bit (4 bytes)
- 32 bytes = 8 個寄存器 (8 × 4 bytes)
- 31 字元 + 1 byte 長度資訊 = 32 bytes
- 超過此長度需要額外的 global memory 存取，性能下降

---

##### 3. 向量化處理 (Vectorization)

現代 GPU 支援 SIMD（Single Instruction Multiple Data）指令：

```c
// 一般模式：逐個字元處理
for (int i = 0; i < len; i++) {
    result[i] = transform(password[i]);
}

// 優化模式：向量化處理（一次處理 4 個字元）
uint32_vec4 data = load_vec4(password);  // 一次讀取 4 bytes
uint32_vec4 result = transform_vec4(data); // 同時處理 4 個字元
```

**效能提升**：
- 一次指令處理 4 個字元而非 1 個
- 記憶體頻寬利用率提升 4 倍
- GPU 並行度更高

---

##### 4. 編譯器最佳化 (Compiler Optimization)

因為密碼長度在編譯時期已知，編譯器可進行：

| 優化技術 | 說明 | 效能影響 |
|---------|------|---------|
| **Loop Unrolling** | 將迴圈完全展開 | 消除分支預測失敗 |
| **Constant Propagation** | 預先計算常數表達式 | 減少運算指令數 |
| **Dead Code Elimination** | 移除不可能執行的程式碼路徑 | 減少指令快取負擔 |
| **Instruction Scheduling** | 重排指令順序避免流水線停滯 | 提升 IPC（每週期指令數） |
| **Register Allocation** | 最佳化寄存器分配 | 減少記憶體存取 |

---

---

##### 6. 為何不總是啟用 -O？

**記憶體成本**：
- 每種密碼長度需要獨立的 kernel（1-31 共需 31 個 kernels）
- 每個 kernel 約 200-500 KB
- 總共需要額外 6-15 MB GPU 記憶體

**編譯時間**：
- 首次執行需要編譯 31 個不同長度的 kernels
- 編譯時間約 10-30 秒（依 GPU 而定）
- 後續執行會使用快取（存於 `kernels/` 目錄）

**彈性犧牲**：
- 無法破解超過 31 字元的密碼
- 某些複雜 hash（如 bcrypt）的優化效果有限

---

## Mode 3: Mask Attack (純遮罩攻擊)

### 基本概念
使用「遮罩」(mask) 定義密碼的字符集和位置，進行窮舉式暴力破解。

### 完整指令格式
```bash
hashcat -m <hash_type> -a 3 <hash_file> <mask> [可選參數]
```

**必要參數**：
- `-m <hash_type>`：Hash 類型（如 100 = SHA-1）
- `-a 3`：攻擊模式 3（Mask Attack）
- `<hash_file>`：包含 hash 的檔案
- `<mask>`：密碼遮罩（如 `?l?l?d?d`）

**可選參數**：
- `-d 1`：指定 GPU
- `-w 4`：工作負載模式
- `-O`：啟用優化核心
- `-1 <charset>`：自定義字符集 1
- `--hex-charset`：使用 hex 編碼字符集
- `--status --status-json`：狀態監控

### 遮罩字符集

| 符號 | 代表字符集 | 範例 | 數量 |
|------|-----------|------|------|
| `?l` | 小寫字母 | a-z | 26 |
| `?u` | 大寫字母 | A-Z | 26 |
| `?d` | 數字 | 0-9 | 10 |
| `?s` | 特殊字符 | 空格!"#$%&'()*+,-./:;<=>?@[\]^_`{\|}~ | 33 |
| `?a` | 全部可見字符 | ?l + ?u + ?d + ?s | 95 |
| `?b` | 全部字節 | 0x00-0xff | 256 |
| `?1`-`?4` | 自定義字符集 1-4 | 使用者定義 | 自訂 |

#### 範例 1：簡單 Mask Attack

**目標密碼**：`pass1234`（4 個小寫字母 + 4 個數字）

```bash
hashcat -m 100 -a 3 -d 1 -w 4 hash.txt ?l?l?l?l?d?d?d?d
```

**參數說明**：
- `-m 100`：SHA-1 hash
- `-a 3`：Mask Attack 模式
- `-d 1`：使用 GPU 1
- `-w 4`：Nightmare 工作負載
- `hash.txt`：包含目標 hash 的檔案
- `?l?l?l?l?d?d?d?d`：4 個小寫字母 + 4 個數字

**搜索空間**：26⁴ × 10⁴ = 456,976 × 10,000 = 4,569,760,000（約 45.7 億）

#### 範例 2：混合大小寫與數字

**目標密碼**：`Pass123`（大寫+3小寫+3數字）

```bash
hashcat -m 100 -a 3 -d 1 -w 4 hash.txt ?u?l?l?l?d?d?d
```

**搜索空間**：26 × 26³ × 10³ = 456,976,000（約 4.57 億）

#### 範例 3：自定義特殊字符集

**目標密碼**：`test12#@`（4 小寫 + 2 數字 + 2 特殊字符 `#@!^%$&`）

**方法 1：使用 hex 格式（推薦）**
```bash
hashcat -m 100 -a 3 -d 1 -w 4 -O --hex-charset -1 2340215e25245e26 hash.txt ?l?l?l?l?d?d?1?1
```

**參數說明**：
- `--hex-charset`：使用 hex 格式定義字符集（避免 Shell 轉義問題）
- `-1 2340215e252426`：自定義字符集 1 = `#@!^%$&`（hex 編碼）
  - `23` = `#`
  - `40` = `@`
  - `21` = `!`
  - `5e` = `^`
  - `25` = `%`
  - `24` = `$`
  - `5e` = `^`
  - `26` = `&`
- `?1?1`：使用自定義字符集 1 的兩個字符

**方法 2：使用純文字格式**
```bash
hashcat -m 100 -a 3 -d 1 -w 4 -1 "#@!^%$&" hash.txt ?l?l?l?l?d?d?1?1
```

**注意**：純文字格式可能需要 Shell 轉義，建議使用 hex 格式。

#### 範例 4：增量 Mask Attack

**目標**：破解 6-8 位純數字密碼

```bash
# 方法 1：逐一執行
hashcat -m 100 -a 3 hash.txt ?d?d?d?d?d?d
hashcat -m 100 -a 3 hash.txt ?d?d?d?d?d?d?d
hashcat -m 100 -a 3 hash.txt ?d?d?d?d?d?d?d?d

# 方法 2：使用增量模式
hashcat -m 100 -a 3 --increment --increment-min=6 --increment-max=8 hash.txt ?d?d?d?d?d?d?d?d
```

**參數說明**：
- `--increment`：啟用增量模式
- `--increment-min=6`：從 6 位開始
- `--increment-max=8`：到 8 位結束

#### 範例 5：多個自定義字符集

**目標密碼**：第一位必須大寫，最後兩位是特定符號 `!@#`

```bash
hashcat -m 100 -a 3 -1 ABCDEFG -2 "!@#" hash.txt ?1?l?l?l?l?d?d?2?2
```

**參數說明**：
- `-1 ABCDEFG`：自定義字符集 1 = 特定大寫字母
- `-2 "!@#"`：自定義字符集 2 = 特定符號
- `?1`：第一位使用字符集 1
- `?2?2`：最後兩位使用字符集 2

---

## Mode 0: Dictionary Attack (字典攻擊)

### 基本概念
使用預先準備的密碼字典檔案，逐一嘗試字典中的每個密碼。

### 完整指令格式
```bash
hashcat -m <hash_type> -a 0 <hash_file> <dictionary_file> [可選參數]
```

**必要參數**：
- `-m <hash_type>`：Hash 類型
- `-a 0`：攻擊模式 0（Dictionary Attack）
- `<hash_file>`：包含 hash 的檔案
- `<dictionary_file>`：字典檔案

**可選參數**：
- `-d 1 -w 4`：GPU 與工作負載設定
- `-r <rule_file>`：使用規則檔案
- `-O`：啟用優化核心

#### 範例 1：基本字典攻擊

```bash
hashcat -m 100 -a 0 -d 1 -w 4 hash.txt dictionary.txt
```

**參數說明**：
- `-a 0`：Dictionary Attack 模式
- `dictionary.txt`：包含密碼列表的檔案（每行一個密碼）

#### 範例 2：使用規則 (Rules)

```bash
hashcat -m 100 -a 0 -d 1 -w 4 -r rules/best64.rule hash.txt dictionary.txt
```

**規則功能**：大小寫轉換、添加數字後綴、字符替換等

### 其他字典攻擊模式（精簡）

**多個字典檔案**：
```bash
hashcat -m 100 -a 0 hash.txt dict1.txt dict2.txt dict3.txt
```

**組合攻擊 (Mode 1)**：合併兩個字典的單詞
```bash
hashcat -m 100 -a 1 hash.txt dict1.txt dict2.txt
# 範例：pass + 123 → pass123
```

---

## Mode 6: Hybrid Attack (字典+遮罩)

### 基本概念
將字典中的單詞與 mask 進行組合，字典在前、mask 在後。

### 完整指令格式
```bash
hashcat -m <hash_type> -a 6 <hash_file> <dictionary_file> <mask> [可選參數]
```

**必要參數**：
- `-m <hash_type>`：Hash 類型
- `-a 6`：攻擊模式 6（Hybrid Dict+Mask）
- `<hash_file>`：包含 hash 的檔案
- `<dictionary_file>`：字典檔案
- `<mask>`：密碼遮罩（如 `?d?d`）

**可選參數**：
- `-d 1 -w 4 -O`：效能優化設定
- `-1 <charset>`：自定義字符集
- `--hex-charset`：使用 hex 編碼

#### 範例 1：字典 + 數字後綴

**目標密碼**：`password99`（字典單詞 + 2 位數字）

```bash
hashcat -m 100 -a 6 -d 1 -w 4 hash.txt dictionary.txt ?d?d
```

**參數說明**：
- `-a 6`：Hybrid Attack (Dict+Mask)
- `dictionary.txt`：基礎單詞列表
- `?d?d`：添加 2 位數字後綴

**搜索空間**：字典條目數 × 100（00-99）

#### 範例 2：字典 + 年份

**目標密碼**：`admin2024`

```bash
hashcat -m 100 -a 6 -d 1 -w 4 hash.txt dictionary.txt ?d?d?d?d
```

**搜索空間**：字典條目數 × 10,000（0000-9999）

#### 範例 3：字典 + 特殊字符

**目標密碼**：`secure!@`（字典單詞 + 2 個特殊字符）

```bash
hashcat -m 100 -a 6 -d 1 -w 4 --hex-charset -1 2340215e25245e26 hash.txt dictionary.txt ?1?1
```

#### 範例 4：字典 + 複雜後綴

**目標密碼**：`mypass1@`（字典 + 1 數字 + 1 特殊字符）

```bash
hashcat -m 100 -a 6 -d 1 -w 4 -1 "!@#$" hash.txt dictionary.txt ?d?1
```

#### 範例 5：本實驗實際使用

**實驗設定**：
- 字典：`dictionary_splits/combined_dict.txt`（後 30% 切分）
- Mask：從 CSV 動態讀取

```bash
hashcat -m 100 -a 6 -d 1 -w 4 -O hash.txt dictionary_splits/combined_dict.txt ?d?d
```

---

## Mode 7: Hybrid Attack (遮罩+字典)

### 基本概念
將 mask 與字典單詞組合，**mask 在前、字典在後**（與 Mode 6 相反）。

### 完整指令格式
```bash
hashcat -m <hash_type> -a 7 <hash_file> <mask> <dictionary_file> [可選參數]
```

**必要參數**：
- `-m <hash_type>`：Hash 類型
- `-a 7`：攻擊模式 7（Hybrid Mask+Dict）
- `<hash_file>`：包含 hash 的檔案
- `<mask>`：密碼遮罩（如 `?d?d`）
- `<dictionary_file>`：字典檔案

**可選參數**：同 Mode 6

### 範例：數字/特殊字符前綴 + 字典

**目標密碼**：`99password`, `2024admin`, `!@secure`

```bash
# 數字前綴
hashcat -m 100 -a 7 -d 1 -w 4 hash.txt ?d?d dictionary.txt

# 年份前綴
hashcat -m 100 -a 7 hash.txt ?d?d?d?d dictionary.txt

# 特殊字符前綴
hashcat -m 100 -a 7 -1 "!@#$" hash.txt ?1?1 dictionary.txt
```

**注意**：本實驗主要使用 Mode 6（字典+mask），Mode 7 用於密碼前綴為數字/符號的情境。

---

## 進階參數設定

### 1. 效能優化參數（本實驗使用）

```bash
# 指定使用的 GPU
hashcat -d 1 ...  # 使用 GPU 1 (RTX 5070)

# 調整工作負載
hashcat -w 4 ...  # Nightmare 模式（最高效能）

# 啟用優化核心
hashcat -O ...  # 限制密碼長度 ≤31，速度提升 1.5-2 倍
```

### 2. 狀態監控參數（本實驗使用）

```bash
# 以 JSON 格式輸出狀態（便於 Python 程式解析）
hashcat --status --status-json --status-timer=60 ...

# 本實驗實際指令
hashcat -m 100 -a 3 -d 1 -w 4 -O --status --status-json --status-timer=60 hash.txt ?l?l?d?d
```

### 3. 自定義字符集（本實驗使用）

```bash
# 使用 hex 編碼定義特殊字符集（避免 Shell 轉義問題）
hashcat --hex-charset -1 2340215e252426 ...

# 本實驗特殊字符集：#@!^%$& 
# 十六進制編碼：2340215e252426
hashcat --hex-charset -1 2340215e252426 hash.txt ?l?l?d?d?1?1
```

### 4. 其他常用參數

```bash
# 查看可用設備
hashcat -I

# 輸出破解結果到檔案
hashcat -o results.txt ...

# 顯示已破解的密碼
hashcat --show hash.txt

# 效能測試（benchmark）
hashcat -b -m 100

# 計算搜索空間大小
hashcat --keyspace -a 3 ?l?l?l?l?d?d

# 設定執行時間限制（秒）
hashcat --runtime=54000 ...  # 15 小時
```

### 5. 本實驗完整指令範例

**Mask Attack (Mode 3)**：
```bash
hashcat -m 100 -a 3 -d 1 -w 4 -O --status --status-json --status-timer=60 \
  --hex-charset -1 2340215e252426 hash.txt ?l?l?l?l?d?d?1?1
```

**Hybrid Attack (Mode 6)**：
```bash
hashcat -m 100 -a 6 -d 1 -w 4 -O --status --status-json --status-timer=60 \
  --hex-charset -1 2340215e252426 hash.txt dictionary_splits/combined_dict.txt ?d?d?1
```

---

## 搜索空間計算

### 計算公式

**Mask Attack**：
```
搜索空間 = 字符集大小₁ × 字符集大小₂ × ... × 字符集大小ₙ
```

**範例**：
- `?l?l?l?l?d?d` = 26 × 26 × 26 × 26 × 10 × 10 = 45,697,600
- `?u?l?l?l?d?d?s` = 26 × 26³ × 10² × 33 = 1,508,598,400

**Hybrid Attack**：
```
搜索空間 = 字典條目數 × Mask 搜索空間
```

**範例**：
- 字典 100 萬條 + `?d?d` = 1,000,000 × 100 = 100,000,000

### 時間估算




---

## 參考資源

- **官方文件**: https://hashcat.net/wiki/
- **範例 Hash**: https://hashcat.net/wiki/doku.php?id=example_hashes
- **規則語法**: https://hashcat.net/wiki/doku.php?id=rule_based_attack
- **效能測試**: `hashcat -b`

---

**文件版本**: v1.0  
**最後更新**: 2025-12-04  
**適用於**: Hashcat 7.1.2  
**實驗專案**: 密碼破解效能實驗
