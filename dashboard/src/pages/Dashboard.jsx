import React from 'react'
import { Activity, Clock, Shield, Zap, TrendingUp, Target, Cpu, HardDrive } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  // 實驗統計數據
  const stats = [
    {
      icon: Shield,
      title: '測試輪次',
      value: '2',
      subtitle: 'Round 1 & 2',
      color: 'primary'
    },
    {
      icon: Target,
      title: '測試密碼數量',
      value: '100+',
      subtitle: 'Test Cases',
      color: 'success'
    },
    {
      icon: Clock,
      title: '最長破解時間',
      value: '196789s',
      subtitle: 'Max Time (11位)',
      color: 'info'
    },
    {
      icon: Zap,
      title: '峰值速度',
      value: '18.8 GH/s',
      subtitle: 'Peak Speed',
      color: 'warning'
    }
  ]

  // 測試配置分布
  const testConfig = [
    { label: 'Hash 類型', value: 'SHA-1 (m=100)' },
    { label: '測試設備', value: 'NVIDIA RTX 5070' },
    { label: '工作負載', value: 'Nightmare (-w 4)' },
    { label: '優化模式', value: '已啟用 (-O)' },
    { label: '攻擊模式', value: 'Mask Attack Only' }
  ]

  // 實驗研究重點
  const experimentFocus = [
    {
      title: '長度影響分析',
      description: '測試 8-12 位密碼破解時間',
      icon: '📏',
      details: ['觀察長度增加對時間的影響', '計算邊際時間增長']
    },
    {
      title: '特殊字符影響',
      description: '固定長度下增加特殊字符',
      icon: '🔣',
      details: ['基礎長度: 8, 9, 10 字符', '特殊字符: +1 至 +4', '分析邊際時間變化']
    },
    {
      title: '字符種類影響',
      description: '不同字符集組合的效能',
      icon: '🎯',
      details: ['Level 1-3 多樣性分析', '單一/混合字符集比較']
    },
    {
      title: '字符位置影響',
      description: '特殊字符位置對時間的影響',
      icon: '📍',
      details: ['前綴 vs 後綴比較', '混合位置分析']
    }
  ]

  // 密碼長度分布
  const lengthStats = [
    { length: '8', count: 20, percentage: 25 },
    { length: '9', count: 20, percentage: 25 },
    { length: '10', count: 20, percentage: 25 },
    { length: '11', count: 15, percentage: 18.75 },
    { length: '12', count: 15, percentage: 18.75 }
  ]

  return (
    <div className="dashboard fade-in">
      {/* 頂部統計卡片 */}
      <div className="stats-grid">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className={`stat-card stat-${stat.color}`}>
              <div className="stat-icon">
                <Icon size={28} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-title">{stat.title}</div>
                <div className="stat-subtitle">{stat.subtitle}</div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 主要內容區域 */}
      <div className="dashboard-grid">
        {/* 系統配置 */}
        <div className="card system-config">
          <div className="card-title">
            <Cpu size={20} />
            系統配置
          </div>
          <div className="config-list">
            {testConfig.map((config, index) => (
              <div key={index} className="config-item">
                <span className="config-label">{config.label}</span>
                <span className="config-value">{config.value}</span>
              </div>
            ))}
          </div>
          <div className="gpu-status">
            <div className="gpu-icon">
              <HardDrive />
            </div>
            <div className="gpu-info">
              <div className="gpu-temp">溫度: 67°C</div>
              <div className="gpu-util">使用率: 100%</div>
            </div>
          </div>
        </div>

        {/* 實驗研究重點 */}
        <div className="card attack-modes">
          <div className="card-title">
            <Activity size={20} />
            實驗研究重點
          </div>
          <div className="mode-list">
            {experimentFocus.map((focus, index) => (
              <div key={index} className="mode-item">
                <div className="mode-header">
                  <span className="mode-icon">{focus.icon}</span>
                  <div className="mode-info">
                    <div className="mode-name">{focus.title}</div>
                    <div className="mode-code">{focus.description}</div>
                  </div>
                </div>
                <ul className="focus-details">
                  {focus.details.map((detail, i) => (
                    <li key={i}>{detail}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* 測試配置分布 */}
        <div className="card length-distribution">
          <div className="card-title">
            <TrendingUp size={20} />
            測試配置分布
          </div>
          <div className="test-config-grid">
            <div className="config-box">
              <div className="config-number">5</div>
              <div className="config-label">長度測試</div>
              <div className="config-detail">8, 9, 10, 11, 12 位</div>
            </div>
            <div className="config-box">
              <div className="config-number">4</div>
              <div className="config-label">特殊字符測試</div>
              <div className="config-detail">8+1, 8+2, 8+3, 8+4</div>
            </div>
            <div className="config-box">
              <div className="config-number">3</div>
              <div className="config-label">字符種類</div>
              <div className="config-detail">單一/雙重/多重</div>
            </div>
            <div className="config-box">
              <div className="config-number">3</div>
              <div className="config-label">字符位置</div>
              <div className="config-detail">前綴/後綴/混合</div>
            </div>
          </div>
        </div>

        {/* 實驗階段 */}
        <div className="card experiment-phases">
          <div className="card-title">
            <Target size={20} />
            實驗階段
          </div>
          <div className="phases-timeline">
            <div className="phase completed">
              <div className="phase-dot"></div>
              <div className="phase-content">
                <div className="phase-title">Round 1 - Firsttest</div>
                <div className="phase-desc">基礎長度測試 (8-12 位)</div>
                <span className="badge badge-success">已完成</span>
              </div>
            </div>
            <div className="phase completed">
              <div className="phase-dot"></div>
              <div className="phase-content">
                <div className="phase-title">Round 1 - Secondtest</div>
                <div className="phase-desc">特殊字符增量測試 (8+1 到 8+4)</div>
                <span className="badge badge-success">已完成</span>
              </div>
            </div>
            <div className="phase completed">
              <div className="phase-dot"></div>
              <div className="phase-content">
                <div className="phase-title">Round 2 - 驗證測試</div>
                <div className="phase-desc">重複測試以驗證數據一致性</div>
                <span className="badge badge-success">已完成</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 關鍵發現 */}
      <div className="card key-findings">
        <div className="card-title">
          <Zap size={20} />
          關鍵發現
        </div>
        <div className="findings-grid">
          <div className="finding-item">
            <div className="finding-icon">�</div>
            <div className="finding-text">
              <strong>長度指數增長效應</strong>
              <p>密碼長度每增加 1 位，破解時間呈指數級增長，邊際時間增加 26 倍</p>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🔣</div>
            <div className="finding-text">
              <strong>特殊字符邊際成本</strong>
              <p>增加特殊字符顯著增加破解時間，8+4 比 8+1 慢數十倍</p>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🎯</div>
            <div className="finding-text">
              <strong>字符種類多樣性關鍵</strong>
              <p>Level 3 (多種字符) 比 Level 1 (單一字符) 破解時間增加數百倍</p>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">📍</div>
            <div className="finding-text">
              <strong>字符位置影響有限</strong>
              <p>前綴、後綴、混合位置的破解時間差異不大，主要由字符種類決定</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
