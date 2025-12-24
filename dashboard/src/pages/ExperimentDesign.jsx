import React, { useState } from 'react'
import { FileText, Target, Settings, Info, Layers, Cpu, Zap, Shield } from 'lucide-react'
import './ExperimentDesign.css'

function ExperimentDesign() {
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="experiment-design fade-in">
      {/* Header */}
      <div className="design-header">
        <h1>實驗設計方案</h1>
        <p>Hashcat 密碼破解效能分析完整實驗設計</p>
      </div>

      {/* Tabs */}
      <div className="design-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Target size={18} />
          實驗概述
        </button>
        <button 
          className={`tab-btn ${activeTab === 'methodology' ? 'active' : ''}`}
          onClick={() => setActiveTab('methodology')}
        >
          <Layers size={18} />
          測試方法
        </button>
        <button 
          className={`tab-btn ${activeTab === 'config' ? 'active' : ''}`}
          onClick={() => setActiveTab('config')}
        >
          <Settings size={18} />
          系統配置
        </button>
        <button 
          className={`tab-btn ${activeTab === 'parameters' ? 'active' : ''}`}
          onClick={() => setActiveTab('parameters')}
        >
          <Info size={18} />
          參數說明
        </button>
      </div>

      {/* Content */}
      <div className="design-content">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'methodology' && <MethodologyTab />}
        {activeTab === 'config' && <ConfigTab />}
        {activeTab === 'parameters' && <ParametersTab />}
      </div>
    </div>
  )
}

function OverviewTab() {
  const objectives = [
    {
      icon: '📏',
      title: '長度影響分析',
      description: '量化分析密碼長度增加對破解時間的影響，計算邊際時間成本'
    },
    {
      icon: '🔣',
      title: '特殊字符影響',
      description: '測試增加特殊字符數量（8+1至8+4）對破解時間的邊際影響'
    },
    {
      icon: '🎨',
      title: '字符種類多樣性',
      description: '分析不同字符類型組合（Level 1-3）對破解難度的影響'
    },
    {
      icon: '📍',
      title: '字符位置影響',
      description: '研究特殊字符位置（前綴/後綴/混合）對破解時間的影響'
    }
  ];

  const rounds = [
    {
      round: 'Round 1',
      title: '基礎測試與變化分析',
      tests: [
        'Firsttest: 密碼長度測試 (8, 9, 10, 11, 12 字符)',
        'Secondtest: 特殊字符數量測試 (8+1, 8+2, 8+3, 8+4)',
        '使用 Mask Attack 模式，記錄破解時間'
      ],
      status: 'completed'
    },
    {
      round: 'Round 2',
      title: '驗證與深入分析',
      tests: [
        'Firsttest: 字符種類多樣性測試 (Level 1/2/3)',
        'Secondtest: 特殊字符位置影響測試 (prefix/suffix/mixed)',
        '使用 Mask Attack 模式，深入分析影響因素'
      ],
      status: 'completed'
    }
  ];

  return (
    <div className="overview-tab">
      {/* Objectives */}
      <div className="card">
        <div className="card-title">
          <Target size={20} />
          實驗目標
        </div>
        <div className="objectives-grid">
          {objectives.map((obj, index) => (
            <div key={index} className="objective-card">
              <div className="obj-icon">{obj.icon}</div>
              <div className="obj-title">{obj.title}</div>
              <div className="obj-desc">{obj.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Rounds */}
      <div className="card">
        <div className="card-title">
          <Layers size={20} />
          測試輪次設計
        </div>
        <div className="rounds-list">
          {rounds.map((round, index) => (
            <div key={index} className="round-card">
              <div className="round-header">
                <div className="round-badge">{round.round}</div>
                <div className="round-title">{round.title}</div>
                <span className={`badge badge-${round.status === 'completed' ? 'success' : 'info'}`}>
                  {round.status === 'completed' ? '已完成' : '進行中'}
                </span>
              </div>
              <ul className="round-tests">
                {round.tests.map((test, i) => (
                  <li key={i}>{test}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Key Variables */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          研究變數
        </div>
        <div className="variables-grid">
          <div className="variable-item">
            <div className="var-label">獨立變數</div>
            <ul className="var-list">
              <li>密碼長度 (8, 9, 10, 11, 12 字符)</li>
              <li>特殊字符數量 (8+1, 8+2, 8+3, 8+4)</li>
              <li>字符種類多樣性 (Level 1/2/3)</li>
              <li>特殊字符位置 (prefix/suffix/mixed)</li>
            </ul>
          </div>
          <div className="variable-item">
            <div className="var-label">依變數</div>
            <ul className="var-list">
              <li>破解時間 (秒)</li>
              <li>邊際時間成本</li>
              <li>破解速度 (Hash/s)</li>
              <li>搜索空間大小</li>
            </ul>
          </div>
          <div className="variable-item">
            <div className="var-label">控制變數</div>
            <ul className="var-list">
              <li>攻擊模式: Mask Attack (Mode 3)</li>
              <li>Hash 類型: SHA-1 (m 100)</li>
              <li>GPU 設備: RTX 5070</li>
              <li>工作負載: Nightmare (-w 4)</li>
              <li>優化模式: 已啟用 (-O)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

function MethodologyTab() {
  const attackModes = [
    {
      mode: 'Mode 3',
      name: 'Mask Attack (Brute Force)',
      description: '使用遮罩定義字符集進行暴力破解，適合已知密碼格式的場景',
      command: 'hashcat -m 100 -a 3 hash.txt ?l?l?l?l?l?l?a?a?a?a -w 4 -O',
      pros: ['可覆蓋所有可能組合', '適合已知密碼格式', '可精確控制搜索空間', '效率高且可預測'],
      cons: ['時間隨長度指數增長', '不適合超長密碼', '需要事先了解密碼模式']
    }
  ];

  const testDesign = [
    {
      round: 'Round 1 - Firsttest',
      focus: '密碼長度影響',
      details: [
        '測試長度: 8, 9, 10, 11, 12 字符',
        '字符集: 小寫字母 + 數字 (basic8.txt ~ basic12.txt)',
        '目標: 觀察長度增加對破解時間的影響',
        '分析: 計算每增加一個字符的邊際時間成本'
      ]
    },
    {
      round: 'Round 1 - Secondtest',
      focus: '特殊字符數量影響',
      details: [
        '基礎長度: 8, 9, 10 字符',
        '特殊字符數量: +1, +2, +3, +4',
        '目標: 分析在不同基礎長度下增加特殊字符的影響',
        '分析: 計算每增加一個特殊字符的邊際時間成本'
      ]
    },
    {
      round: 'Round 2 - Firsttest',
      focus: '字符種類多樣性',
      details: [
        'Level 1: 單一字符類型 (純小寫/純數字)',
        'Level 2: 兩種字符類型 (小寫+數字)',
        'Level 3: 多種字符類型 (小寫+大寫+數字+特殊)',
        '分析: 字符集多樣性對搜索空間和破解時間的影響'
      ]
    },
    {
      round: 'Round 2 - Secondtest',
      focus: '特殊字符位置影響',
      details: [
        'Prefix: 特殊字符在開頭',
        'Suffix: 特殊字符在結尾',
        'Mixed: 特殊字符分散在中間',
        '分析: 特殊字符位置是否影響破解順序和時間'
      ]
    }
  ];

  const maskCharsets = [
    { symbol: '?l', description: '小寫字母', example: 'a-z', count: 26 },
    { symbol: '?u', description: '大寫字母', example: 'A-Z', count: 26 },
    { symbol: '?d', description: '數字', example: '0-9', count: 10 },
    { symbol: '?s', description: '特殊符號', example: '!@#$%...', count: 33 },
    { symbol: '?a', description: '所有可見字符', example: 'l+u+d+s', count: 95 },
    { symbol: '?b', description: '所有字節', example: '0x00-0xFF', count: 256 }
  ]

  return (
    <div className="methodology-tab">
      {/* Attack Modes */}
      <div className="card">
        <div className="card-title">
          <Shield size={20} />
          攻擊模式
        </div>
        <div className="attack-modes-detail">
          {attackModes.map((mode, index) => (
            <div key={index} className="attack-mode-card">
              <div className="mode-header-detail">
                <span className="mode-badge">{mode.mode}</span>
                <h3>{mode.name}</h3>
              </div>
              <p className="mode-description">{mode.description}</p>
              <div className="mode-command">
                <code>{mode.command}</code>
              </div>
              <div className="pros-cons">
                <div className="pros">
                  <strong>優點：</strong>
                  <ul>
                    {mode.pros.map((pro, i) => (
                      <li key={i}>✓ {pro}</li>
                    ))}
                  </ul>
                </div>
                <div className="cons">
                  <strong>限制：</strong>
                  <ul>
                    {mode.cons.map((con, i) => (
                      <li key={i}>✗ {con}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Design */}
      <div className="card">
        <div className="card-title">
          <Layers size={20} />
          測試設計詳情
        </div>
        <div className="test-design-list">
          {testDesign.map((test, index) => (
            <div key={index} className="test-design-card">
              <div className="test-header">
                <span className="test-round-badge">{test.round}</span>
                <h3>{test.focus}</h3>
              </div>
              <ul className="test-details">
                {test.details.map((detail, i) => (
                  <li key={i}>{detail}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Mask Charsets */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          遮罩字符集說明
        </div>
        <div className="charset-table">
          <table>
            <thead>
              <tr>
                <th>符號</th>
                <th>描述</th>
                <th>範例</th>
                <th>字符數</th>
              </tr>
            </thead>
            <tbody>
              {maskCharsets.map((charset, index) => (
                <tr key={index}>
                  <td><code className="charset-symbol">{charset.symbol}</code></td>
                  <td>{charset.description}</td>
                  <td className="charset-example">{charset.example}</td>
                  <td><span className="charset-count">{charset.count}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Example */}
      <div className="card">
        <div className="card-title">
          <FileText size={20} />
          遮罩範例解析
        </div>
        <div className="mask-examples">
          <div className="example-item">
            <div className="example-mask"><code>?l?l?l?l?l?l?a?a?a?a</code></div>
            <div className="example-desc">
              <div className="desc-line">
                <span className="highlight-green">?l × 6</span> = 前 6 位小寫字母 (a-z)
              </div>
              <div className="desc-line">
                <span className="highlight-blue">?a × 4</span> = 後 4 位所有可見字符
              </div>
              <div className="desc-line">
                總搜索空間: <strong>26⁶ × 95⁴ ≈ 6.49 × 10¹⁴</strong> 種組合
              </div>
            </div>
          </div>
          <div className="example-item">
            <div className="example-mask"><code>?u?l?l?l?l?l?l?l?d?d</code></div>
            <div className="example-desc">
              <div className="desc-line">
                <span className="highlight-green">?u × 1</span> = 首位大寫字母
              </div>
              <div className="desc-line">
                <span className="highlight-blue">?l × 7</span> = 中間 7 位小寫字母
              </div>
              <div className="desc-line">
                <span className="highlight-yellow">?d × 2</span> = 末尾 2 位數字
              </div>
              <div className="desc-line">
                總搜索空間: <strong>26 × 26⁷ × 10² ≈ 8.03 × 10¹²</strong> 種組合
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ConfigTab() {
  const systemSpecs = [
    { label: 'GPU 型號', value: 'NVIDIA GeForce RTX 5070', icon: <Cpu /> },
    { label: 'CUDA 核心', value: '未指定', icon: <Zap /> },
    { label: 'GPU 記憶體', value: '未指定', icon: <Shield /> },
    { label: '驅動版本', value: '最新版本', icon: <Settings /> }
  ]

  const hashcatConfig = [
    { param: '-m 100', description: 'Hash 類型: SHA-1 (160-bit)' },
    { param: '-a [0/3/6/7]', description: '攻擊模式: 字典/遮罩/混合' },
    { param: '-w 4', description: '工作負載: Nightmare (100% GPU)' },
    { param: '-O', description: '優化核心: 啟用 (速度提升 1.5-2x)' },
    { param: '--force', description: '強制執行: 忽略警告' },
    { param: '--status', description: '顯示狀態: 即時監控' },
    { param: '--status-json', description: 'JSON 輸出: 便於數據收集' },
    { param: '--status-timer=60', description: '狀態更新間隔: 60 秒' }
  ]

  const optimizations = [
    {
      title: '優化核心 (-O)',
      description: '使用特化版本的 GPU kernel，速度提升 1.5-2 倍',
      impact: '+50% ~ +100% 速度',
      limitation: '密碼長度限制 ≤ 31 字符'
    },
    {
      title: 'Nightmare 模式 (-w 4)',
      description: 'GPU 使用率達到 100%，最大化運算效能',
      impact: '最高效能',
      limitation: '系統可能反應緩慢'
    },
    {
      title: 'JSON 狀態輸出',
      description: '結構化數據輸出，便於自動化分析',
      impact: '提升數據處理效率',
      limitation: '無'
    }
  ]

  return (
    <div className="config-tab">
      {/* System Specs */}
      <div className="card">
        <div className="card-title">
          <Cpu size={20} />
          硬體配置
        </div>
        <div className="specs-grid">
          {systemSpecs.map((spec, index) => (
            <div key={index} className="spec-item">
              <div className="spec-icon">{spec.icon}</div>
              <div className="spec-content">
                <div className="spec-label">{spec.label}</div>
                <div className="spec-value">{spec.value}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hashcat Config */}
      <div className="card">
        <div className="card-title">
          <Settings size={20} />
          Hashcat 參數配置
        </div>
        <div className="config-table">
          {hashcatConfig.map((config, index) => (
            <div key={index} className="config-row">
              <code className="param-code">{config.param}</code>
              <div className="param-desc">{config.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Optimizations */}
      <div className="card">
        <div className="card-title">
          <Zap size={20} />
          效能優化策略
        </div>
        <div className="optimizations-list">
          {optimizations.map((opt, index) => (
            <div key={index} className="optimization-card">
              <h3>{opt.title}</h3>
              <p>{opt.description}</p>
              <div className="opt-details">
                <div className="opt-impact">
                  <span className="opt-label">效能影響:</span>
                  <span className="opt-value success">{opt.impact}</span>
                </div>
                <div className="opt-limitation">
                  <span className="opt-label">限制條件:</span>
                  <span className="opt-value">{opt.limitation}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ParametersTab() {
  const workloadModes = [
    { mode: '1', name: 'Low', gpu: '~50%', response: '流暢', scenario: '日常使用電腦時' },
    { mode: '2', name: 'Default', gpu: '~75%', response: '正常', scenario: '預設值' },
    { mode: '3', name: 'High', gpu: '~90%', response: '稍慢', scenario: '專注破解時' },
    { mode: '4', name: 'Nightmare', gpu: '~100%', response: '可能卡頓', scenario: '專用破解機 (本實驗使用)' }
  ]

  const performanceFactors = [
    {
      factor: '密碼長度',
      impact: '高',
      description: '每增加 1 位，搜索空間乘以字符集大小',
      example: '8 位→9 位，時間增加 26-95 倍'
    },
    {
      factor: '字符複雜度',
      impact: '高',
      description: '字符種類越多，搜索空間越大',
      example: '純小寫 (26) vs 全字符 (95)'
    },
    {
      factor: '攻擊模式',
      impact: '中',
      description: '不同模式效率差異顯著',
      example: '字典模式通常比暴力破解快 30%+'
    },
    {
      factor: '優化參數',
      impact: '中',
      description: '-O 參數可提升 1.5-2 倍速度',
      example: '10 小時 → 5-7 小時'
    },
    {
      factor: 'GPU 性能',
      impact: '中',
      description: 'GPU 運算能力直接影響破解速度',
      example: 'RTX 5070: ~18.8 GH/s'
    }
  ]

  return (
    <div className="parameters-tab">
      {/* Workload Modes */}
      <div className="card">
        <div className="card-title">
          <Settings size={20} />
          工作負載模式 (-w)
        </div>
        <div className="workload-table">
          <table>
            <thead>
              <tr>
                <th>模式</th>
                <th>名稱</th>
                <th>GPU 使用率</th>
                <th>系統回應</th>
                <th>適用場景</th>
              </tr>
            </thead>
            <tbody>
              {workloadModes.map((wl, index) => (
                <tr key={index} className={wl.mode === '4' ? 'highlight-row' : ''}>
                  <td><code>{wl.mode}</code></td>
                  <td><strong>{wl.name}</strong></td>
                  <td>{wl.gpu}</td>
                  <td>{wl.response}</td>
                  <td>{wl.scenario}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Factors */}
      <div className="card">
        <div className="card-title">
          <Zap size={20} />
          效能影響因素
        </div>
        <div className="factors-list">
          {performanceFactors.map((factor, index) => (
            <div key={index} className="factor-card">
              <div className="factor-header">
                <h3>{factor.factor}</h3>
                <span className={`impact-badge impact-${factor.impact === '高' ? 'high' : 'medium'}`}>
                  影響: {factor.impact}
                </span>
              </div>
              <p className="factor-desc">{factor.description}</p>
              <div className="factor-example">
                <strong>範例:</strong> {factor.example}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Formula */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          搜索空間計算
        </div>
        <div className="formula-section">
          <div className="formula-card">
            <h3>基本公式</h3>
            <div className="formula">
              搜索空間 = 字符集大小<sup>密碼長度</sup>
            </div>
            <div className="formula-example">
              <p><strong>範例 1:</strong> 8 位純小寫密碼</p>
              <p className="calculation">= 26<sup>8</sup> = 208,827,064,576 ≈ 2.09 × 10<sup>11</sup></p>
            </div>
            <div className="formula-example">
              <p><strong>範例 2:</strong> 10 位全字符密碼</p>
              <p className="calculation">= 95<sup>10</sup> = 59,873,693,923,837,890,625 ≈ 5.99 × 10<sup>19</sup></p>
            </div>
          </div>
          <div className="formula-card">
            <h3>預估破解時間</h3>
            <div className="formula">
              時間 (秒) = 搜索空間 ÷ GPU 速度 (Hash/s)
            </div>
            <div className="formula-example">
              <p><strong>以 RTX 5070 為例</strong> (速度: 18.8 GH/s = 1.88 × 10<sup>10</sup> H/s)</p>
              <p className="calculation">8 位小寫: 2.09 × 10<sup>11</sup> ÷ 1.88 × 10<sup>10</sup> ≈ 11.1 秒</p>
              <p className="calculation">10 位全字符: 5.99 × 10<sup>19</sup> ÷ 1.88 × 10<sup>10</sup> ≈ 101 年</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExperimentDesign
