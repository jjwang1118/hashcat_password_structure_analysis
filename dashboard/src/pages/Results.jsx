import React, { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart, ComposedChart, Cell } from 'recharts'
import { TrendingUp, BarChart3, Clock, Zap, Info, Activity, CheckCircle } from 'lucide-react'
import './Results.css'

// 響應式圖表高度 Hook
function useResponsiveHeight(desktopHeight) {
  const [height, setHeight] = useState(desktopHeight)

  useEffect(() => {
    const updateHeight = () => {
      if (window.innerWidth <= 480) {
        setHeight(desktopHeight * 0.7) // 小屏幕減少30%
      } else if (window.innerWidth <= 768) {
        setHeight(desktopHeight * 0.85) // 平板減少15%
      } else {
        setHeight(desktopHeight)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)
    return () => window.removeEventListener('resize', updateHeight)
  }, [desktopHeight])

  return height
}

function Results() {
  const [activeCategory, setActiveCategory] = useState('length')

  return (
    <div className="results fade-in">
      {/* Header */}
      <div className="results-header">
        <h1>實驗數據結果分析</h1>
        <p>基於三輪實驗的綜合數據分析與關鍵發現</p>
      </div>

      {/* Category Tabs */}
      <div className="category-tabs">
        <button 
          className={`category-btn ${activeCategory === 'length' ? 'active' : ''}`}
          onClick={() => setActiveCategory('length')}
        >
          <TrendingUp size={18} />
          長度影響分析
        </button>
        <button 
          className={`category-btn ${activeCategory === 'special' ? 'active' : ''}`}
          onClick={() => setActiveCategory('special')}
        >
          <BarChart3 size={18} />
          特殊字符影響
        </button>
        <button 
          className={`category-btn ${activeCategory === 'diversity' ? 'active' : ''}`}
          onClick={() => setActiveCategory('diversity')}
        >
          <Activity size={18} />
          字符種類影響
        </button>
        <button 
          className={`category-btn ${activeCategory === 'position' ? 'active' : ''}`}
          onClick={() => setActiveCategory('position')}
        >
          <Zap size={18} />
          位置影響分析
        </button>
        <button 
          className={`category-btn ${activeCategory === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveCategory('summary')}
        >
          <CheckCircle size={18} />
          總結報告
        </button>
      </div>

      {/* Content */}
      <div className="results-content">
        {activeCategory === 'length' && <LengthAnalysis />}
        {activeCategory === 'special' && <SpecialCharAnalysis />}
        {activeCategory === 'diversity' && <DiversityAnalysis />}
        {activeCategory === 'position' && <PositionAnalysis />}
        {activeCategory === 'summary' && <Summary />}
      </div>
    </div>
  )
}

function LengthAnalysis() {
  const [selectedRound, setSelectedRound] = React.useState('total');
  const chartHeight = useResponsiveHeight(450);
  
  // 自定義箱型圖組件
  const BoxPlot = (props) => {
    const { x, y, width, height, payload, index } = props;
    if (!payload || !payload.min) return null;
    
    const { min, q1, med, q3, max, avg } = payload;
    
    // 對數刻度轉換函數
    const yScale = (value) => {
      const logMin = Math.log10(10); // Y軸最小值 10
      const logMax = Math.log10(100000); // Y軸最大值 100000
      const logValue = Math.log10(Math.max(value, 10));
      const ratio = (logValue - logMin) / (logMax - logMin);
      return y + height * (1 - ratio);
    };
    
    const centerX = x + width / 2;
    const boxWidth = width * 0.5;
    const boxLeft = centerX - boxWidth / 2;
    const boxRight = centerX + boxWidth / 2;
    
    // 計算各點的 Y 座標
    const minY = yScale(min);
    const q1Y = yScale(q1);
    const medY = yScale(med);
    const q3Y = yScale(q3);
    const maxY = yScale(max);
    const avgY = yScale(avg);
    
    return (
      <g>
        {/* 下鬚線 (min to Q1) */}
        <line 
          x1={centerX} 
          y1={minY} 
          x2={centerX} 
          y2={q1Y} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最小值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={minY} 
          x2={centerX + 10} 
          y2={minY} 
          stroke="#00ccff" 
          strokeWidth={2}
        />
        
        {/* 箱體 (Q1 to Q3) */}
        <rect 
          x={boxLeft} 
          y={q3Y} 
          width={boxWidth} 
          height={Math.max(q1Y - q3Y, 1)} 
          fill="#8884d8" 
          fillOpacity={0.7}
          stroke="#5566cc"
          strokeWidth={2}
        />
        
        {/* 中位數線 */}
        <line 
          x1={boxLeft} 
          y1={medY} 
          x2={boxRight} 
          y2={medY} 
          stroke="#ffd700" 
          strokeWidth={3}
        />
        
        {/* 上鬚線 (Q3 to max) */}
        <line 
          x1={centerX} 
          y1={q3Y} 
          x2={centerX} 
          y2={maxY} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最大值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={maxY} 
          x2={centerX + 10} 
          y2={maxY} 
          stroke="#ff6b6b" 
          strokeWidth={2}
        />
        
        {/* 平均值點 */}
        <circle 
          cx={centerX} 
          cy={avgY} 
          r={5} 
          fill="#00ff88" 
          stroke="#fff" 
          strokeWidth={2}
        />
      </g>
    );
  };
  
  // 實際數據：密碼長度 vs 破解時間 (Mask Attack)
  const allRoundData = {
    'round1': [
      { length: '8', time: 13.29, min: 12.57, q1: 12.78, med: 12.79, q3: 13.56, max: 15.84, avg: 13.29, n: 10, searches: 208827064576 },
      { length: '9', time: 31.83, min: 12.74, q1: 13.04, med: 13.81, q3: 26.90, max: 96.49, avg: 31.83, n: 10, searches: 5429503678976 },
      { length: '10', time: 285.50, min: 12.75, q1: 48.11, med: 97.15, q3: 511.41, max: 954.68, avg: 285.50, n: 10, searches: 141167095653376 },
      { length: '11', time: 3939.87, min: 1420.24, q1: 1848.55, med: 3060.84, q3: 5970.30, max: 7399.42, avg: 3939.87, n: 5, searches: 3670344486987776 },
      { length: '12', time: 17693.57, min: 1766.21, q1: 2979.14, med: 4385.56, q3: 5998.49, max: 73338.46, avg: 17693.57, n: 5, searches: 95428956661682176 }
    ],
    'round2': [
      { length: '8', time: 14.85, min: 12.44, q1: 14.31, med: 14.46, q3: 15.43, max: 18.43, avg: 14.85, n: 10, searches: 208827064576 },
      { length: '9', time: 14.51, min: 11.53, q1: 14.38, med: 14.40, q3: 15.17, max: 17.07, avg: 14.51, n: 10, searches: 5429503678976 },
      { length: '10', time: 19.22, min: 12.44, q1: 14.41, med: 14.91, q3: 25.43, max: 32.43, avg: 19.22, n: 10, searches: 141167095653376 },
      { length: '11', time: 2379.73, min: 144.99, q1: 1594.76, med: 2857.52, q3: 3082.68, max: 4218.69, avg: 2379.73, n: 5, searches: 3670344486987776 },
      { length: '12', time: 22179.35, min: 2525.36, q1: 2878.58, med: 7647.20, q3: 47801.07, max: 50044.56, avg: 22179.35, n: 5, searches: 95428956661682176 }
    ],
    'total': [
      { length: '8', time: 14.07, min: 12.44, q1: 12.78, med: 13.91, q3: 14.75, max: 18.43, avg: 14.07, n: 20, searches: 208827064576 },
      { length: '9', time: 23.17, min: 11.53, q1: 13.51, med: 14.39, q3: 16.80, max: 96.49, avg: 23.17, n: 20, searches: 5429503678976 },
      { length: '10', time: 152.36, min: 12.44, q1: 14.43, med: 28.95, q3: 81.14, max: 954.68, avg: 152.36, n: 20, searches: 141167095653376 },
      { length: '11', time: 3159.80, min: 144.99, q1: 1658.21, med: 2959.18, q3: 3934.69, max: 7399.42, avg: 3159.80, n: 10, searches: 3670344486987776 },
      { length: '12', time: 19936.46, min: 1766.21, q1: 2903.72, med: 5192.02, q3: 37762.60, max: 73338.46, avg: 19936.46, n: 10, searches: 95428956661682176 }
    ]
  };
  
  const lengthTimeData = allRoundData[selectedRound];

  // 邊際時間分析 - 使用平均值計算
  const marginalData = lengthTimeData.filter((d, index) => index > 0).map((d, index) => ({
    length: `${parseInt(lengthTimeData[index].length)}→${d.length}`,
    marginal: d.avg - lengthTimeData[index].avg,
    ratio: (d.avg / lengthTimeData[index].avg),
    growthRate: ((d.avg / lengthTimeData[index].avg - 1) * 100).toFixed(1) + '%',
    baseLength: parseInt(lengthTimeData[index].length),
    targetLength: parseInt(d.length),
    absMargin: Math.abs(d.avg - lengthTimeData[index].avg) // 用於圖表顯示的絕對值
  }));
  
  // 檢查是否有負值邊際時間
  const hasNegativeMargin = marginalData.some(d => d.marginal < 0);
  const useLogScale = !hasNegativeMargin && marginalData.every(d => d.marginal >= 0.1);

  const getRoundLabel = () => {
    switch(selectedRound) {
      case 'round1': return 'Round 1';
      case 'round2': return 'Round 2';
      case 'total': return 'Round 1 & Round 2 合併';
      default: return '';
    }
  };

  return (
    <div className="length-analysis">
      {/* Round 選擇器 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          選擇測試輪次
        </div>
        <div className="length-selector">
          <button 
            className={`length-btn ${selectedRound === 'round1' ? 'active' : ''}`}
            onClick={() => setSelectedRound('round1')}
          >
            Round 1
          </button>
          <button 
            className={`length-btn ${selectedRound === 'round2' ? 'active' : ''}`}
            onClick={() => setSelectedRound('round2')}
          >
            Round 2
          </button>
          <button 
            className={`length-btn ${selectedRound === 'total' ? 'active' : ''}`}
            onClick={() => setSelectedRound('total')}
          >
            Total (合併)
          </button>
        </div>
      </div>

      {/* 破解時間 vs 長度 */}
      <div className="card chart-card">
        <div className="card-title">
          <Clock size={20} />
          密碼長度對破解時間的影響 ({getRoundLabel()})
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>樣本數: {lengthTimeData.map(d => `${d.length}字符=${d.n}個`).join(', ')}</span>
        </div>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart data={lengthTimeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="length" 
              stroke="#888" 
              label={{ value: '密碼長度 (字符)', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              stroke="#888" 
              scale="log"
              domain={[10, 100000]}
              tickFormatter={(value) => value.toLocaleString()}
              label={{ value: '破解時間 (秒, 對數刻度)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '200px' }}>
                      <p style={{ color: '#fff', margin: '0 0 10px 0', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
                        密碼長度: {data.length} 字符
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#ff6b6b' }}>最大值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.max.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#82ca9d' }}>Q3 (75%):</span>
                        <span style={{ color: '#fff' }}>{data.q3.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', background: '#2a2a2a', padding: '4px 8px', marginLeft: '-8px', marginRight: '-8px' }}>
                        <span style={{ color: '#ffd700' }}>中位數:</span>
                        <span style={{ color: '#ffd700', fontWeight: 'bold' }}>{data.med.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ff88' }}>平均值:</span>
                        <span style={{ color: '#00ff88', fontWeight: 'bold' }}>{data.avg.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#8884d8' }}>Q1 (25%):</span>
                        <span style={{ color: '#fff' }}>{data.q1.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ccff' }}>最小值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.min.toFixed(2)}s</span>
                      </div>
                      <div style={{ borderTop: '1px solid #444', marginTop: '8px', paddingTop: '8px', display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#999', fontSize: '11px' }}>IQR:</span>
                        <span style={{ color: '#999', fontSize: '11px' }}>{(data.q3 - data.q1).toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#999', fontSize: '11px' }}>樣本數:</span>
                        <span style={{ color: '#999', fontSize: '11px' }}>n={data.n}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar 
              dataKey="max" 
              fill="transparent" 
              shape={<BoxPlot />}
            />
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>箱型圖說明:</strong> 📦 藍色箱體 = Q1~Q3 四分位距 | ─ 金色線 = 中位數 | ⚪ 綠色圓點 = 平均值 | ┊ 虛線 = whiskers
          </div>
          <div className="insight-item">
            <strong>樣本數:</strong> {lengthTimeData[0].n} 至 {lengthTimeData[lengthTimeData.length-1].n} 個測試
          </div>
          <div className="insight-item">
            <strong>趨勢:</strong> 密碼長度增加導致破解時間呈指數級增長
          </div>
        </div>
      </div>

      {/* 邊際時間成本 */}
      <div className="card chart-card">
        <div className="card-title">
          <TrendingUp size={20} />
          長度增加的邊際時間成本 ({getRoundLabel()})
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>每增加一個字符的額外時間成本與增長率</span>
        </div>
        <ResponsiveContainer width="100%" height={chartHeight * 0.9}>
          <BarChart data={marginalData} margin={{ top: 30, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="length" 
              stroke="#888"
              label={{ value: '長度變化', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              stroke="#888"
              scale={useLogScale ? "log" : "linear"}
              domain={useLogScale ? [0.1, 'auto'] : ['auto', 'auto']}
              label={{ value: useLogScale ? '邊際時間 (秒, 對數刻度)' : '邊際時間 (秒)', angle: -90, position: 'insideLeft', fill: '#888' }}
              tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(1)}k` : value >= 1 ? value.toFixed(0) : value.toFixed(1)}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '220px' }}>
                      <p style={{ color: '#fff', margin: '0 0 10px 0', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
                        {data.baseLength} → {data.targetLength} 字符
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '6px 0' }}>
                        <span style={{ color: '#00ccff' }}>邊際時間:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.marginal >= 0 ? '+' : ''}{data.marginal.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '6px 0', background: '#2a2a2a', padding: '6px', marginLeft: '-8px', marginRight: '-8px' }}>
                        <span style={{ color: '#0f0' }}>增長率:</span>
                        <span style={{ color: '#0f0', fontWeight: 'bold' }}>{data.growthRate}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Bar 
              dataKey="marginal" 
              fill="#00ccff" 
              name="邊際時間差異"
              label={{ 
                position: 'top', 
                fill: '#00ccff', 
                formatter: (value) => {
                  const absValue = Math.abs(value);
                  const sign = value >= 0 ? '' : '-';
                  return sign + (absValue >= 1000 ? `${(absValue/1000).toFixed(1)}k` : absValue >= 1 ? `${absValue.toFixed(0)}s` : `${absValue.toFixed(1)}s`);
                },
                fontSize: 11
              }}
            />
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>趨勢:</strong> 邊際時間成本呈指數級增長，長度越長增加的成本越高
          </div>
          <div className="insight-item">
            <strong>最大增幅:</strong> {marginalData[marginalData.length-1]?.length} 的邊際時間為 {marginalData[marginalData.length-1]?.marginal.toFixed(1)}秒 (增長{marginalData[marginalData.length-1]?.growthRate})
          </div>
        </div>
      </div>

      {/* 長度增加詳細數據表格 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          長度增加邊際時間詳細數據
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  長度變化
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  邊際時間 (秒)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  增長率
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  樣本數
                </th>
              </tr>
            </thead>
            <tbody>
              {marginalData.map((row, idx) => (
                <tr 
                  key={idx} 
                  style={{ 
                    background: idx % 2 === 0 ? 'rgba(0, 204, 255, 0.03)' : 'transparent',
                    borderBottom: '1px solid var(--border-color)'
                  }}
                >
                  <td style={{ padding: '12px', color: 'var(--text-primary)', fontWeight: 500 }}>
                    {row.baseLength} → {row.targetLength} 字符
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right', 
                    color: 'var(--accent-secondary)', 
                    fontWeight: 600 
                  }}>
                    +{row.marginal.toFixed(2)}s
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right', 
                    color: '#00ff88',
                    fontWeight: 600
                  }}>
                    {row.growthRate}
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right', 
                    color: 'var(--text-secondary)'
                  }}>
                    {lengthTimeData.find(d => d.length === row.targetLength)?.n || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="chart-insights" style={{ marginTop: '1rem' }}>
          <div className="insight-item">
            <strong>說明:</strong> 邊際時間 = 當前長度平均時間 - 前一長度平均時間
          </div>
          <div className="insight-item">
            <strong>數據來源:</strong> {getRoundLabel()} 的完整數據集
          </div>
        </div>
      </div>

      {/* 在固定特殊字符數量下，長度增加的邊際時間成本 */}
      <div className="card chart-card">
        <div className="card-title">
          <TrendingUp size={20} />
          在固定特殊字符數量下，增加密碼長度對破解時間的影響
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>比較不同特殊字符數量時，基礎長度從 8→9 和 9→10 的邊際時間成本</span>
        </div>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <ComposedChart 
            data={[
              { specialChars: '+1', transition89: 38.8, transition910: 354.1, growth89: 275.0, growth910: 669.4 },
              { specialChars: '+2', transition89: 32.6, transition910: 530.6, growth89: 209.0, growth910: 1101.7 },
              { specialChars: '+3', transition89: 43.8, transition910: 739.5, growth89: 283.3, growth910: 1248.6 },
              { specialChars: '+4', transition89: 53.5, transition910: 495.9, growth89: 364.3, growth910: 727.0 }
            ]}
            margin={{ top: 20, right: 60, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="specialChars" 
              stroke="#888"
              label={{ value: '特殊字符數量', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              yAxisId="left"
              stroke="#888"
              scale="log"
              domain={[10, 1000]}
              label={{ value: '邊際時間 (秒, 對數刻度)', angle: -90, position: 'insideLeft', fill: '#888' }}
              tickFormatter={(value) => value >= 100 ? `${value}s` : `${value.toFixed(0)}s`}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#ffa500"
              domain={[0, 1500]}
              label={{ value: '增長率 (%)', angle: 90, position: 'insideRight', fill: '#ffa500' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '240px' }}>
                      <p style={{ color: '#fff', margin: '0 0 10px 0', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
                        特殊字符: {data.specialChars}
                      </p>
                      <div style={{ marginBottom: '8px', paddingBottom: '8px', borderBottom: '1px solid #333' }}>
                        <p style={{ color: '#0af', margin: '4px 0', fontSize: '13px' }}>8→9 字符:</p>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', paddingLeft: '12px' }}>
                          <span style={{ color: '#888' }}>邊際時間:</span>
                          <span style={{ color: '#fff', fontWeight: 'bold' }}>+{data.transition89}s</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', paddingLeft: '12px' }}>
                          <span style={{ color: '#888' }}>增長率:</span>
                          <span style={{ color: '#ffa500', fontWeight: 'bold' }}>{data.growth89}%</span>
                        </div>
                      </div>
                      <div>
                        <p style={{ color: '#f5a', margin: '4px 0', fontSize: '13px' }}>9→10 字符:</p>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', paddingLeft: '12px' }}>
                          <span style={{ color: '#888' }}>邊際時間:</span>
                          <span style={{ color: '#fff', fontWeight: 'bold' }}>+{data.transition910}s</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', paddingLeft: '12px' }}>
                          <span style={{ color: '#888' }}>增長率:</span>
                          <span style={{ color: '#ffa500', fontWeight: 'bold' }}>{data.growth910}%</span>
                        </div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="transition89" fill="#0af" name="8→9 邊際時間" />
            <Bar yAxisId="left" dataKey="transition910" fill="#f5a" name="9→10 邊際時間" />
            <Line yAxisId="right" type="monotone" dataKey="growth910" stroke="#ffa500" strokeWidth={3} dot={{ r: 5 }} name="9→10 增長率" strokeDasharray="5 5" />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>關鍵發現:</strong> 9→10 的邊際時間遠大於 8→9，且隨特殊字符數量變化有不同表現
          </div>
          <div className="insight-item">
            <strong>最高增長:</strong> +3 特殊字符時，9→10 的邊際時間達 739.5s，增長率 1248.6%
          </div>
        </div>
      </div>

      {/* 長度轉換詳細數據表格 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          固定特殊字符下的長度增加詳細數據
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  特殊字符數量
                </th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 600 }}>
                  基礎長度轉換
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  時間差異 (秒)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  增長率
                </th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ background: 'rgba(78, 205, 196, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', color: 'var(--text-secondary)' }} rowSpan="2">+1</td>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>8→9</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#0af', fontWeight: 600 }}>+38.8s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>275.0%</td>
              </tr>
              <tr style={{ background: 'rgba(78, 205, 196, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>9→10</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#f5a', fontWeight: 600 }}>+354.1s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>669.4%</td>
              </tr>
              
              <tr style={{ background: 'rgba(255, 107, 107, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', color: 'var(--text-secondary)' }} rowSpan="2">+2</td>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>8→9</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#0af', fontWeight: 600 }}>+32.6s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>209.0%</td>
              </tr>
              <tr style={{ background: 'rgba(255, 107, 107, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>9→10</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#f5a', fontWeight: 600 }}>+530.6s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>1101.7%</td>
              </tr>
              
              <tr style={{ background: 'rgba(255, 193, 7, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', color: 'var(--text-secondary)' }} rowSpan="2">+3</td>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>8→9</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#0af', fontWeight: 600 }}>+43.8s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>283.3%</td>
              </tr>
              <tr style={{ background: 'rgba(255, 193, 7, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>9→10</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#f5a', fontWeight: 600 }}>+739.5s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>1248.6%</td>
              </tr>
              
              <tr style={{ background: 'rgba(149, 117, 205, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', color: 'var(--text-secondary)' }} rowSpan="2">+4</td>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>8→9</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#0af', fontWeight: 600 }}>+53.5s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>364.3%</td>
              </tr>
              <tr style={{ background: 'rgba(149, 117, 205, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>9→10</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#f5a', fontWeight: 600 }}>+495.9s</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>727.0%</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="chart-insights" style={{ marginTop: '1rem' }}>
          <div className="insight-item">
            <strong>說明:</strong> 固定特殊字符數量，比較密碼長度增加時的邊際時間成本
          </div>
          <div className="insight-item">
            <strong>數據來源:</strong> Round 1 Secondtest 實驗數據
          </div>
        </div>
      </div>

      {/* 關鍵發現 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          關鍵發現
        </div>
        <div className="findings-list">
          <div className="finding-item">
            <div className="finding-icon">📈</div>
            <div className="finding-content">
              <div className="finding-title">指數級增長</div>
              <div className="finding-desc">密碼長度從 8 增加到 12 字符，破解時間從 11.2 秒增長到 5,116,514 秒（約 59 天），增長超過 45 萬倍</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">⚡</div>
            <div className="finding-content">
              <div className="finding-title">邊際成本遞增</div>
              <div className="finding-desc">
                每增加一個字符的邊際時間成本呈指數增長：8→9 (+{marginalData[0]?.marginal.toFixed(1)}s, {marginalData[0]?.growthRate})，
                11→12 (+{marginalData[3]?.marginal.toFixed(0)}s, {marginalData[3]?.growthRate})
              </div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🎯</div>
            <div className="finding-content">
              <div className="finding-title">安全建議</div>
              <div className="finding-desc">密碼長度是最有效的安全防護措施，建議最少使用 11-12 字符以上的密碼</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SpecialCharAnalysis() {
  const [selectedLength, setSelectedLength] = React.useState('8');
  const [selectedRound, setSelectedRound] = React.useState('total');
  const chartHeight = useResponsiveHeight(380);
  
  // 完整的箱型圖數據 (包含 min, q1, med, q3, max, avg, n)
  const allRoundData = {
    round1: {
      '8': [
        { specialChars: 1, min: 12.72, q1: 12.95, med: 13.74, q3: 13.79, max: 16.76, avg: 13.72, n: 10 },
        { specialChars: 2, min: 12.73, q1: 12.77, med: 13.71, q3: 14.51, max: 22.83, avg: 14.46, n: 10 },
        { specialChars: 3, min: 12.74, q1: 12.82, med: 13.78, q3: 15.12, max: 16.75, avg: 14.13, n: 10 },
        { specialChars: 4, min: 12.73, q1: 12.75, med: 13.71, q3: 13.75, max: 15.77, avg: 13.64, n: 10 }
      ],
      '9': [
        { specialChars: 1, min: 12.78, q1: 27.42, med: 44.07, q3: 50.17, max: 79.38, avg: 41.94, n: 10 },
        { specialChars: 2, min: 12.69, q1: 27.65, med: 35.95, q3: 41.49, max: 245.72, avg: 58.92, n: 10 },
        { specialChars: 3, min: 12.76, q1: 22.81, med: 45.56, q3: 96.68, max: 162.93, avg: 62.85, n: 10 },
        { specialChars: 4, min: 12.7, q1: 15.53, med: 32.4, q3: 43.77, max: 336.44, avg: 59.83, n: 10 }
      ],
      '10': [
        { specialChars: 1, min: 14.41, q1: 29.66, med: 54.63, q3: 65.8, max: 165.1, avg: 58.42, n: 10 },
        { specialChars: 2, min: 16.44, q1: 42.28, med: 58.28, q3: 186.67, max: 440.46, avg: 128.41, n: 10 },
        { specialChars: 3, min: 31.87, q1: 218.63, med: 627.61, q3: 933.43, max: 1414.36, avg: 619.5, n: 10 },
        { specialChars: 4, min: 23.82, q1: 411.38, med: 490.47, q3: 604.63, max: 1437.03, avg: 605.93, n: 10 }
      ]
    },
    round2: {
      '8': [
        { specialChars: 1, min: 12.68, q1: 12.71, med: 13.74, q3: 14.74, max: 21.75, avg: 14.49, n: 10 },
        { specialChars: 2, min: 12.71, q1: 13.74, med: 15.71, q3: 19.7, max: 22.82, avg: 16.72, n: 10 },
        { specialChars: 3, min: 12.68, q1: 12.87, med: 13.58, q3: 14.28, max: 45.03, avg: 16.77, n: 10 },
        { specialChars: 4, min: 12.71, q1: 13.79, med: 16.12, q3: 17.78, max: 17.84, avg: 15.74, n: 10 }
      ],
      '9': [
        { specialChars: 1, min: 17.72, q1: 26.66, med: 51.95, q3: 66.57, max: 228.94, avg: 63.85, n: 10 },
        { specialChars: 2, min: 12.69, q1: 23.48, med: 27.7, q3: 48.94, max: 78.73, avg: 37.4, n: 10 },
        { specialChars: 3, min: 12.68, q1: 24.4, med: 33.33, q3: 77.79, max: 143.41, avg: 55.61, n: 10 },
        { specialChars: 4, min: 12.74, q1: 35.84, med: 64.82, q3: 117.13, max: 173.87, avg: 76.59, n: 10 }
      ],
      '10': [
        { specialChars: 1, min: 23.52, q1: 62.27, med: 233.76, q3: 1162.19, max: 2698.1, avg: 755.52, n: 10 },
        { specialChars: 2, min: 13.76, q1: 494.98, med: 965.7, q3: 1488.61, max: 2606.4, avg: 1029.06, n: 10 },
        { specialChars: 3, min: 38.72, q1: 308.73, med: 760.91, q3: 1354.43, max: 2966.0, avg: 978.06, n: 10 },
        { specialChars: 4, min: 15.8, q1: 100.96, med: 163.57, q3: 317.87, max: 2682.12, avg: 522.25, n: 10 }
      ]
    },
    total: {
      '8': [
        { specialChars: 1, min: 12.68, q1: 12.76, med: 13.74, q3: 14.02, max: 21.75, avg: 14.11, n: 20 },
        { specialChars: 2, min: 12.71, q1: 12.77, med: 13.75, q3: 17.7, max: 22.83, avg: 15.59, n: 20 },
        { specialChars: 3, min: 12.68, q1: 12.79, med: 13.76, q3: 14.93, max: 45.03, avg: 15.45, n: 20 },
        { specialChars: 4, min: 12.71, q1: 13.44, med: 13.76, q3: 16.22, max: 17.84, avg: 14.69, n: 20 }
      ],
      '9': [
        { specialChars: 1, min: 12.78, q1: 23.62, med: 48.49, q3: 57.86, max: 228.94, avg: 52.9, n: 20 },
        { specialChars: 2, min: 12.69, q1: 24.89, med: 31.95, q3: 45.04, max: 245.72, avg: 48.16, n: 20 },
        { specialChars: 3, min: 12.68, q1: 23.66, med: 35.43, q3: 89.28, max: 162.93, avg: 59.23, n: 20 },
        { specialChars: 4, min: 12.7, q1: 21.22, med: 40.46, q3: 74.97, max: 336.44, avg: 68.21, n: 20 }
      ],
      '10': [
        { specialChars: 1, min: 14.41, q1: 41.31, med: 65.61, q3: 207.56, max: 2698.1, avg: 406.97, n: 20 },
        { specialChars: 2, min: 13.76, q1: 44.84, med: 217.78, q3: 853.55, max: 2606.4, avg: 578.74, n: 20 },
        { specialChars: 3, min: 31.87, q1: 223.48, med: 702.29, q3: 1137.16, max: 2966.0, avg: 798.78, n: 20 },
        { specialChars: 4, min: 15.8, q1: 143.88, med: 370.65, q3: 579.47, max: 2682.12, avg: 564.09, n: 20 }
      ]
    }
  };

  const currentData = allRoundData[selectedRound][selectedLength];
  
  const getRoundLabel = () => {
    if (selectedRound === 'round1') return 'Round 1';
    if (selectedRound === 'round2') return 'Round 2';
    return 'Round 1 & Round 2 合併';
  };

  // 自定義 BoxPlot 組件
  const BoxPlot = ({ x, y, width, height, payload, index }) => {
    const data = currentData[index];
    if (!data) return null;

    const scaleY = (value) => {
      if (value <= 0) return height;
      const logValue = Math.log10(value);
      const logMin = 0; // log10(1) = 0
      const logMax = Math.log10(Math.max(...currentData.map(d => d.max)) * 1.2);
      const ratio = (logValue - logMin) / (logMax - logMin);
      return height - (ratio * height);
    };

    const boxWidth = width * 0.6;
    const centerX = x + width / 2;

    const yMin = scaleY(data.min);
    const yQ1 = scaleY(data.q1);
    const yMed = scaleY(data.med);
    const yQ3 = scaleY(data.q3);
    const yMax = scaleY(data.max);
    const yAvg = scaleY(data.avg);

    return (
      <g>
        {/* 鬚線 (whiskers) */}
        <line x1={centerX} y1={yMin} x2={centerX} y2={yMax} stroke="#666" strokeWidth={1.5} strokeDasharray="4 2" />
        
        {/* 盒子 (Q1 to Q3) */}
        <rect
          x={centerX - boxWidth / 2}
          y={yQ3}
          width={boxWidth}
          height={yQ1 - yQ3}
          fill="#00ccff"
          fillOpacity={0.7}
          stroke="#00ccff"
          strokeWidth={2}
        />
        
        {/* 中位數線 */}
        <line
          x1={centerX - boxWidth / 2}
          y1={yMed}
          x2={centerX + boxWidth / 2}
          y2={yMed}
          stroke="#ff6b00"
          strokeWidth={3}
        />
        
        {/* 平均值點 */}
        <circle cx={centerX} cy={yAvg} r={4} fill="#00ff88" stroke="#fff" strokeWidth={1.5} />
        
        {/* 最小值和最大值標記 */}
        <line x1={centerX - boxWidth / 4} y1={yMin} x2={centerX + boxWidth / 4} y2={yMin} stroke="#666" strokeWidth={2} />
        <line x1={centerX - boxWidth / 4} y1={yMax} x2={centerX + boxWidth / 4} y2={yMax} stroke="#666" strokeWidth={2} />
      </g>
    );
  };

  // 計算邊際時間（每增加一個特殊字符的額外時間）
  const marginalData = currentData.slice(1).map((d, i) => {
    const prevData = currentData[i];
    const marginal = d.avg - prevData.avg;
    const ratio = d.avg / prevData.avg;
    const growthRate = ((d.avg - prevData.avg) / prevData.avg * 100).toFixed(1) + '%';
    return {
      specialChars: `+${d.specialChars}`,
      marginal: marginal,
      ratio: ratio,
      growthRate: growthRate,
      fromCount: prevData.specialChars,
      toCount: d.specialChars
    };
  });

  // 為三個長度準備數據（用於比較圖表）
  const prepareComparisonData = () => {
    const lengths = ['8', '9', '10'];
    const specialCounts = [1, 2, 3, 4];
    
    return specialCounts.map(sc => {
      const dataPoint = { specialChars: sc };
      lengths.forEach(len => {
        const data = allRoundData[selectedRound][len];
        const currentItem = data.find(d => d.specialChars === sc);
        const prevItem = data.find(d => d.specialChars === sc - 1);
        if (currentItem && prevItem) {
          dataPoint[`length${len}`] = currentItem.avg - prevItem.avg;
        } else {
          dataPoint[`length${len}`] = 0;
        }
      });
      return dataPoint;
    });
  };

  const comparisonData = prepareComparisonData();

  // 準備表格數據
  const tableData = [];
  const lengths = ['8', '9', '10'];
  lengths.forEach(len => {
    const data = allRoundData[selectedRound][len];
    for (let i = 1; i < data.length; i++) {
      const current = data[i];
      const prev = data[i - 1];
      const timeDiff = current.avg - prev.avg;
      const growth = ((timeDiff / prev.avg) * 100).toFixed(1);
      tableData.push({
        baseLength: len,
        transition: `+${prev.specialChars}→+${current.specialChars}`,
        timeDiff: timeDiff.toFixed(2),
        growth: growth
      });
    }
  });

  return (
    <div className="special-char-analysis">
      {/* Round 選擇器 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          選擇數據集
        </div>
        <div className="round-selector">
          <button 
            className={`round-btn ${selectedRound === 'round1' ? 'active' : ''}`}
            onClick={() => setSelectedRound('round1')}
          >
            Round 1
          </button>
          <button 
            className={`round-btn ${selectedRound === 'round2' ? 'active' : ''}`}
            onClick={() => setSelectedRound('round2')}
          >
            Round 2
          </button>
          <button 
            className={`round-btn ${selectedRound === 'total' ? 'active' : ''}`}
            onClick={() => setSelectedRound('total')}
          >
            Total
          </button>
        </div>
      </div>

      {/* 長度選擇器 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          選擇基礎長度
        </div>
        <div className="length-selector">
          <button 
            className={`length-btn ${selectedLength === '8' ? 'active' : ''}`}
            onClick={() => setSelectedLength('8')}
          >
            長度 8
          </button>
          <button 
            className={`length-btn ${selectedLength === '9' ? 'active' : ''}`}
            onClick={() => setSelectedLength('9')}
          >
            長度 9
          </button>
          <button 
            className={`length-btn ${selectedLength === '10' ? 'active' : ''}`}
            onClick={() => setSelectedLength('10')}
          >
            長度 10
          </button>
        </div>
      </div>

      {/* 特殊字符數量 vs 時間 (BoxPlot) */}
      <div className="card chart-card">
        <div className="card-title">
          <Clock size={20} />
          特殊字符數量對破解時間的影響 ({getRoundLabel()})
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>基礎長度 {selectedLength} 字符，測試增加 1-4 個特殊字符的影響</span>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={currentData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="specialChars" 
              stroke="#888"
              label={{ value: '特殊字符數量', position: 'insideBottom', offset: -10, fill: '#888' }}
            />
            <YAxis 
              stroke="#888"
              scale="log"
              domain={[1, 'auto']}
              label={{ value: '破解時間 (秒, 對數刻度)', angle: -90, position: 'insideLeft', fill: '#888' }}
              tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(1)}k` : value.toFixed(0)}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '200px' }}>
                      <p style={{ color: '#fff', margin: '0 0 8px 0', fontWeight: 'bold' }}>+{data.specialChars} 特殊字符</p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#888' }}>樣本數:</span>
                        <span style={{ color: '#fff' }}>{data.n}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#888' }}>最小值:</span>
                        <span style={{ color: '#fff' }}>{data.min.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ccff' }}>Q1:</span>
                        <span style={{ color: '#00ccff' }}>{data.q1.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#ff6b00' }}>中位數:</span>
                        <span style={{ color: '#ff6b00', fontWeight: 'bold' }}>{data.med.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ccff' }}>Q3:</span>
                        <span style={{ color: '#00ccff' }}>{data.q3.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#888' }}>最大值:</span>
                        <span style={{ color: '#fff' }}>{data.max.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', paddingTop: '4px', borderTop: '1px solid #444' }}>
                        <span style={{ color: '#00ff88' }}>平均值:</span>
                        <span style={{ color: '#00ff88', fontWeight: 'bold' }}>{data.avg.toFixed(2)}s</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="avg" shape={<BoxPlot />} fill="#00ccff" />
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>趨勢:</strong> 特殊字符數量增加導致破解時間上升，但效果因基礎長度而異
          </div>
          <div className="insight-item">
            <strong>數據說明:</strong> 盒狀圖顯示最小值、Q1、中位數(橙線)、Q3、最大值，綠點為平均值
          </div>
        </div>
      </div>

      {/* 邊際時間成本比較（三個長度） */}
      <div className="card chart-card">
        <div className="card-title">
          <TrendingUp size={20} />
          不同基礎長度的邊際時間比較 ({getRoundLabel()})
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>比較基礎長度 8、9、10 字符在增加特殊字符時的邊際時間成本</span>
        </div>
        <ResponsiveContainer width="100%" height={450}>
          <LineChart data={comparisonData} margin={{ top: 30, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="specialChars" 
              stroke="#888"
              label={{ value: '特殊字符數量', position: 'insideBottom', offset: -10, fill: '#888' }}
              tickFormatter={(value) => `+${value}`}
            />
            <YAxis 
              stroke="#888"
              domain={[0, 'auto']}
              label={{ value: '邊際時間 (秒)', angle: -90, position: 'insideLeft', fill: '#888' }}
              tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(1)}k` : value.toFixed(0)}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              formatter={(value, name) => {
                const lengthMap = { 'length8': '長度 8', 'length9': '長度 9', 'length10': '長度 10' };
                return [`+${value.toFixed(2)}s`, lengthMap[name] || name];
              }}
              labelFormatter={(label) => `特殊字符: +${label}`}
            />
            <Legend 
              formatter={(value) => {
                const map = { 'length8': 'Base Length 8', 'length9': 'Base Length 9', 'length10': 'Base Length 10' };
                return map[value] || value;
              }}
            />
            <Line 
              type="monotone" 
              dataKey="length8" 
              stroke="#ff6b6b" 
              strokeWidth={3} 
              dot={{ r: 5 }} 
              name="length8"
              label={{ 
                position: 'top', 
                fill: '#ff6b6b', 
                formatter: (value) => value >= 0 ? `+${value.toFixed(1)}s` : `${value.toFixed(1)}s`,
                fontSize: 11
              }}
            />
            <Line 
              type="monotone" 
              dataKey="length9" 
              stroke="#4ecdc4" 
              strokeWidth={3} 
              dot={{ r: 5 }} 
              name="length9"
              label={{ 
                position: 'top', 
                fill: '#4ecdc4', 
                formatter: (value) => value >= 0 ? `+${value.toFixed(1)}s` : `${value.toFixed(1)}s`,
                fontSize: 11
              }}
            />
            <Line 
              type="monotone" 
              dataKey="length10" 
              stroke="#95e1d3" 
              strokeWidth={3} 
              dot={{ r: 5 }} 
              name="length10"
              label={{ 
                position: 'top', 
                fill: '#95e1d3', 
                formatter: (value) => value >= 0 ? `+${value.toFixed(1)}s` : `${value.toFixed(1)}s`,
                fontSize: 11
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 邊際時間詳細表格 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          邊際時間詳細數據
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  基礎長度
                </th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 600 }}>
                  特殊字符增加
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  時間差異 (秒)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  增長率
                </th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr 
                  key={idx} 
                  style={{ 
                    background: row.baseLength === '8' ? 'rgba(255, 107, 107, 0.05)' : 
                                row.baseLength === '9' ? 'rgba(78, 205, 196, 0.05)' : 
                                'rgba(149, 225, 211, 0.05)',
                    borderBottom: '1px solid var(--border-color)'
                  }}
                >
                  <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>
                    Base {row.baseLength}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', color: 'var(--text-primary)', fontWeight: 500 }}>
                    {row.transition}
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right', 
                    color: parseFloat(row.timeDiff) >= 0 ? 'var(--accent-secondary)' : '#ff6b6b', 
                    fontWeight: 600 
                  }}>
                    {parseFloat(row.timeDiff) >= 0 ? '+' : ''}{row.timeDiff}s
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right', 
                    color: parseFloat(row.growth) < 0 ? '#ff6b6b' : '#00ff88',
                    fontWeight: 600
                  }}>
                    {row.growth}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 關鍵發現 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          關鍵發現
        </div>
        <div className="findings-list">
          <div className="finding-item">
            <div className="finding-icon">🔣</div>
            <div className="finding-content">
              <div className="finding-title">特殊字符顯著增加破解難度</div>
              <div className="finding-desc">在不同基礎長度（8, 9, 10 字符）下，增加特殊字符都能顯著增加破解時間，基礎長度越長，特殊字符的邊際效益越大</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">📊</div>
            <div className="finding-content">
              <div className="finding-title">邊際效益遞增且與長度相關</div>
              <div className="finding-desc">每增加一個特殊字符的邊際時間成本隨基礎長度呈指數增長，長度 10 的邊際成本遠高於長度 8</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🎯</div>
            <div className="finding-content">
              <div className="finding-title">安全建議</div>
              <div className="finding-desc">結合較長的基礎長度（10+ 字符）與 2-3 個特殊字符，可達到最佳安全性價比</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DiversityAnalysis() {
  const chartHeight = useResponsiveHeight(400);
  
  // 自定義箱型圖組件
  const BoxPlot = (props) => {
    const { x, y, width, height, payload, index } = props;
    if (!payload || !payload.min) return null;
    
    const { min, q1, med, q3, max } = payload;
    
    // 對數刻度轉換函數
    const yScale = (value) => {
      const logMin = Math.log10(10); // Y軸最小值 10
      const logMax = Math.log10(100000); // Y軸最大值 100000
      const logValue = Math.log10(Math.max(value, 10));
      const ratio = (logValue - logMin) / (logMax - logMin);
      return y + height * (1 - ratio);
    };
    
    const centerX = x + width / 2;
    const boxWidth = width * 0.5;
    const boxLeft = centerX - boxWidth / 2;
    const boxRight = centerX + boxWidth / 2;
    
    // 計算各點的 Y 座標
    const minY = yScale(min);
    const q1Y = yScale(q1);
    const medY = yScale(med);
    const q3Y = yScale(q3);
    const maxY = yScale(max);
    
    return (
      <g>
        {/* 下鬚線 (min to Q1) */}
        <line 
          x1={centerX} 
          y1={minY} 
          x2={centerX} 
          y2={q1Y} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最小值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={minY} 
          x2={centerX + 10} 
          y2={minY} 
          stroke="#00ccff" 
          strokeWidth={2}
        />
        
        {/* 箱體 (Q1 to Q3) */}
        <rect 
          x={boxLeft} 
          y={q3Y} 
          width={boxWidth} 
          height={Math.max(q1Y - q3Y, 1)} 
          fill="#8884d8" 
          fillOpacity={0.7}
          stroke="#5566cc"
          strokeWidth={2}
        />
        
        {/* 中位數線 */}
        <line 
          x1={boxLeft} 
          y1={medY} 
          x2={boxRight} 
          y2={medY} 
          stroke="#ffd700" 
          strokeWidth={3}
        />
        
        {/* 上鬚線 (Q3 to max) */}
        <line 
          x1={centerX} 
          y1={q3Y} 
          x2={centerX} 
          y2={maxY} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最大值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={maxY} 
          x2={centerX + 10} 
          y2={maxY} 
          stroke="#ff6b6b" 
          strokeWidth={2}
        />
      </g>
    );
  };

  // 字符種類複雜度數據 (Level 1-3)
  const diversityData = [
    { level: 'Level 1', min: 12.78, q1: 13.81, med: 14.01, q3: 15.43, max: 15.84, n: 7, description: 'Single Charset (純小寫/純大寫)', example: '?l?l?l?l?l?l?l?l 或 ?u?u?u?u?u?u?u?u' },
    { level: 'Level 2', min: 12.78, q1: 12.80, med: 14.40, q3: 1848.55, max: 3060.84, n: 7, description: 'Two Charsets (混合大小寫或字母+數字)', example: '?l?l?u?u?d?d?d?d 或 ?l?l?l?l?d?d?d?d' },
    { level: 'Level 3', min: 2857.52, q1: 2979.14, med: 5998.49, q3: 50044.56, max: 73338.46, n: 7, description: 'Three+ Charsets (包含特殊字符)', example: '?l?u?d?s?s?s?s?s' }
  ];

  return (
    <div className="diversity-analysis">
      {/* 字符種類 vs 破解時間 (箱型圖) */}
      <div className="card chart-card">
        <div className="card-title">
          <Activity size={20} />
          字符種類複雜度對破解時間的影響
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>樣本數: {diversityData.map(d => `${d.level}=${d.n}個`).join(', ')}</span>
        </div>
        <ResponsiveContainer width="100%" height={450}>
          <BarChart data={diversityData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="level" 
              stroke="#888" 
              label={{ value: '字符種類級別', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              stroke="#888" 
              scale="log"
              domain={[10, 100000]}
              tickFormatter={(value) => value.toLocaleString()}
              label={{ value: '破解時間 (秒, 對數刻度)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '200px' }}>
                      <p style={{ color: '#fff', margin: '0 0 10px 0', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
                        {data.level} (n={data.n})
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#ff6b6b' }}>最大值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.max.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#82ca9d' }}>Q3 (75%):</span>
                        <span style={{ color: '#fff' }}>{data.q3.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', background: '#2a2a2a', padding: '4px 8px', marginLeft: '-8px', marginRight: '-8px' }}>
                        <span style={{ color: '#ffd700' }}>中位數:</span>
                        <span style={{ color: '#ffd700', fontWeight: 'bold' }}>{data.med.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#8884d8' }}>Q1 (25%):</span>
                        <span style={{ color: '#fff' }}>{data.q1.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ccff' }}>最小值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.min.toFixed(2)}s</span>
                      </div>
                      <div style={{ borderTop: '1px solid #444', marginTop: '8px', paddingTop: '8px', display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#999', fontSize: '11px' }}>IQR:</span>
                        <span style={{ color: '#999', fontSize: '11px' }}>{(data.q3 - data.q1).toFixed(2)}s</span>
                      </div>
                      <div style={{ borderTop: '1px solid #444', marginTop: '4px', paddingTop: '4px' }}>
                        <div style={{ color: '#aaa', fontSize: '10px', marginTop: '4px' }}>{data.description}</div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar 
              dataKey="max" 
              fill="transparent" 
              shape={<BoxPlot />}
            />
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>箱型圖說明:</strong> 📦 藍色箱體 = Q1~Q3 四分位距 | ─ 金色線 = 中位數 | ┊ 虛線 = whiskers
          </div>
          <div className="insight-item">
            <strong>樣本數:</strong> 每個級別 n=7 個測試
          </div>
          <div className="insight-item">
            <strong>趨勢:</strong> 字符種類複雜度增加導致破解時間呈指數級增長
          </div>
        </div>
      </div>

      {/* 級別詳情 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          字符種類級別詳細說明
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  級別
                </th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  描述
                </th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  範例
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  最小值 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  Q1 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  中位數 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  Q3 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  最大值 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  樣本數
                </th>
              </tr>
            </thead>
            <tbody>
              {diversityData.map((row, idx) => (
                <tr 
                  key={idx}
                  style={{ 
                    borderBottom: '1px solid var(--border-color)',
                    transition: 'background 0.2s',
                    background: idx % 2 === 0 ? 'var(--bg-secondary)' : 'transparent'
                  }}
                >
                  <td style={{ padding: '12px', color: 'var(--text-primary)', fontWeight: 600 }}>
                    {row.level}
                  </td>
                  <td style={{ padding: '12px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {row.description}
                  </td>
                  <td style={{ padding: '12px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                    {row.example}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#00ccff' }}>
                    {row.min.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#8884d8' }}>
                    {row.q1.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#ffd700', fontWeight: 600 }}>
                    {row.med.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#82ca9d' }}>
                    {row.q3.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#ff6b6b' }}>
                    {row.max.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)' }}>
                    n={row.n}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 關鍵發現 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          關鍵發現
        </div>
        <div className="findings-list">
          <div className="finding-item">
            <div className="finding-icon">🎨</div>
            <div className="finding-content">
              <div className="finding-title">字符種類複雜度指數級影響破解時間</div>
              <div className="finding-desc">從 Level 1 (單一字符集) 到 Level 3 (三種以上字符集)，中位數破解時間從 14.01秒 增長到 5998.49秒，增長約 428 倍</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">📊</div>
            <div className="finding-content">
              <div className="finding-title">Level 2 與 Level 3 離散度極大</div>
              <div className="finding-desc">Level 2 的 Q3 達到 1848.55秒，Level 3 的 Q3 達到 50044.56秒，顯示高複雜度密碼破解時間差異極大</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🔒</div>
            <div className="finding-content">
              <div className="finding-title">安全建議：使用多字符集組合</div>
              <div className="finding-desc">建議密碼至少包含 2 種以上字符類型（大小寫字母、數字、特殊字符），Level 3 複雜度可提供最佳安全性</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">⚠️</div>
            <div className="finding-content">
              <div className="finding-title">Level 1 密碼極易破解</div>
              <div className="finding-desc">純小寫或純大寫密碼的破解時間集中在 12-16秒 範圍，安全性極低，應避免使用</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PositionAnalysis() {
  const chartHeight = useResponsiveHeight(450);
  
  // 自定義箱型圖組件
  const BoxPlot = (props) => {
    const { x, y, width, height, payload, index } = props;
    if (!payload || !payload.min) return null;
    
    const { min, q1, med, q3, max, mean } = payload;
    
    // 對數刻度轉換函數
    const yScale = (value) => {
      const logMin = Math.log10(10); // Y軸最小值 10
      const logMax = Math.log10(10000); // Y軸最大值 10000
      const logValue = Math.log10(Math.max(value, 10));
      const ratio = (logValue - logMin) / (logMax - logMin);
      return y + height * (1 - ratio);
    };
    
    const centerX = x + width / 2;
    const boxWidth = width * 0.5;
    const boxLeft = centerX - boxWidth / 2;
    const boxRight = centerX + boxWidth / 2;
    
    // 計算各點的 Y 座標
    const minY = yScale(min);
    const q1Y = yScale(q1);
    const medY = yScale(med);
    const q3Y = yScale(q3);
    const maxY = yScale(max);
    const meanY = yScale(mean);
    
    return (
      <g>
        {/* 下鬚線 (min to Q1) */}
        <line 
          x1={centerX} 
          y1={minY} 
          x2={centerX} 
          y2={q1Y} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最小值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={minY} 
          x2={centerX + 10} 
          y2={minY} 
          stroke="#00ccff" 
          strokeWidth={2}
        />
        
        {/* 箱體 (Q1 to Q3) */}
        <rect 
          x={boxLeft} 
          y={q3Y} 
          width={boxWidth} 
          height={Math.max(q1Y - q3Y, 1)} 
          fill="#8884d8" 
          fillOpacity={0.7}
          stroke="#5566cc"
          strokeWidth={2}
        />
        
        {/* 中位數線 */}
        <line 
          x1={boxLeft} 
          y1={medY} 
          x2={boxRight} 
          y2={medY} 
          stroke="#ffd700" 
          strokeWidth={3}
        />
        
        {/* 上鬚線 (Q3 to max) */}
        <line 
          x1={centerX} 
          y1={q3Y} 
          x2={centerX} 
          y2={maxY} 
          stroke="#666" 
          strokeWidth={1.5} 
          strokeDasharray="3,3"
        />
        {/* 最大值橫線 */}
        <line 
          x1={centerX - 10} 
          y1={maxY} 
          x2={centerX + 10} 
          y2={maxY} 
          stroke="#ff6b6b" 
          strokeWidth={2}
        />
        
        {/* 平均值點 */}
        <circle 
          cx={centerX} 
          cy={meanY} 
          r={5} 
          fill="#00ff88" 
          stroke="#fff" 
          strokeWidth={2}
        />
      </g>
    );
  };

  // 特殊字符位置影響數據 (Round 2 - Secondtest)
  const positionData = [
    { position: 'Prefix', min: 12.68, q1: 13.49, med: 25.59, q3: 79.89, max: 2682.12, mean: 206.84, n: 77, description: '特殊字符在開頭', example: '!@#password' },
    { position: 'Suffix', min: 12.68, q1: 13.71, med: 21.75, q3: 63.03, max: 2966.00, mean: 193.67, n: 77, description: '特殊字符在結尾', example: 'password!@#' },
    { position: 'Mixed', min: 12.68, q1: 17.81, med: 40.99, q3: 241.52, max: 2698.10, mean: 267.50, n: 77, description: '特殊字符分散', example: 'pa!s@sw#ord' }
  ];

  // 平均破解時間數據
  const avgTimeData = positionData.map(d => ({
    position: d.position,
    avgTime: d.mean
  }));

  return (
    <div className="position-analysis">
      {/* 箱型圖：位置 vs 破解時間 */}
      <div className="card chart-card">
        <div className="card-title">
          <Zap size={20} />
          特殊字符位置對破解時間的影響 (箱型圖)
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>樣本數: {positionData.map(d => `${d.position}=${d.n}個`).join(', ')}</span>
        </div>
        <ResponsiveContainer width="100%" height={450}>
          <BarChart data={positionData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="position" 
              stroke="#888" 
              label={{ value: '特殊字符位置', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              stroke="#888" 
              scale="log"
              domain={[10, 10000]}
              tickFormatter={(value) => value.toLocaleString()}
              label={{ value: '破解時間 (秒, 對數刻度)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px', padding: '12px', minWidth: '200px' }}>
                      <p style={{ color: '#fff', margin: '0 0 10px 0', fontWeight: 'bold', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
                        {data.position} (n={data.n})
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#ff6b6b' }}>最大值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.max.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#82ca9d' }}>Q3 (75%):</span>
                        <span style={{ color: '#fff' }}>{data.q3.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0', background: '#2a2a2a', padding: '4px 8px', marginLeft: '-8px', marginRight: '-8px' }}>
                        <span style={{ color: '#ffd700' }}>中位數:</span>
                        <span style={{ color: '#ffd700', fontWeight: 'bold' }}>{data.med.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ff88' }}>平均值:</span>
                        <span style={{ color: '#00ff88', fontWeight: 'bold' }}>{data.mean.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#8884d8' }}>Q1 (25%):</span>
                        <span style={{ color: '#fff' }}>{data.q1.toFixed(2)}s</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '4px 0' }}>
                        <span style={{ color: '#00ccff' }}>最小值:</span>
                        <span style={{ color: '#fff', fontWeight: 'bold' }}>{data.min.toFixed(2)}s</span>
                      </div>
                      <div style={{ borderTop: '1px solid #444', marginTop: '8px', paddingTop: '8px', display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#999', fontSize: '11px' }}>IQR:</span>
                        <span style={{ color: '#999', fontSize: '11px' }}>{(data.q3 - data.q1).toFixed(2)}s</span>
                      </div>
                      <div style={{ borderTop: '1px solid #444', marginTop: '4px', paddingTop: '4px' }}>
                        <div style={{ color: '#aaa', fontSize: '10px', marginTop: '4px' }}>{data.description}</div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar 
              dataKey="max" 
              fill="transparent" 
              shape={<BoxPlot />}
            />
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>箱型圖說明:</strong> 📦 藍色箱體 = Q1~Q3 四分位距 | ─ 金色線 = 中位數 | ⚪ 綠色圓點 = 平均值 | ┊ 虛線 = whiskers
          </div>
          <div className="insight-item">
            <strong>樣本數:</strong> 每個位置 n=77 個測試
          </div>
          <div className="insight-item">
            <strong>觀察:</strong> Mixed 位置的中位數 (40.99s) 和平均值 (267.50s) 較高，破解時間分散度較大
          </div>
        </div>
      </div>

      {/* 長條圖：平均破解時間比較 */}
      <div className="card chart-card">
        <div className="card-title">
          <BarChart3 size={20} />
          平均破解時間比較
        </div>
        <div className="chart-description">
          <Info size={16} />
          <span>比較不同特殊字符位置的平均破解時間</span>
        </div>
        <ResponsiveContainer width="100%" height={chartHeight * 0.78}>
          <BarChart data={avgTimeData} margin={{ top: 30, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="position" 
              stroke="#888"
              label={{ value: '特殊字符位置', position: 'insideBottom', offset: -5, fill: '#888' }}
            />
            <YAxis 
              stroke="#888"
              label={{ value: '平均破解時間 (秒)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '6px' }}
              formatter={(value) => [value.toFixed(2) + ' 秒', '平均破解時間']}
            />
            <Legend />
            <Bar 
              dataKey="avgTime" 
              fill="#00ccff" 
              name="平均破解時間" 
              radius={[8, 8, 0, 0]}
              label={{ 
                position: 'top', 
                fill: '#00ccff', 
                formatter: (value) => `${value.toFixed(1)}s`,
                fontSize: 12
              }}
            >
              {avgTimeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={['#ff6b6b', '#4ecdc4', '#ffd93d'][index]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="chart-insights">
          <div className="insight-item">
            <strong>最快:</strong> Suffix (193.67秒) - 特殊字符在結尾的平均破解時間最短
          </div>
          <div className="insight-item">
            <strong>最慢:</strong> Mixed (267.50秒) - 特殊字符分散的平均破解時間最長，相對安全性略高
          </div>
        </div>
      </div>

      {/* 位置詳情數據表格 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          特殊字符位置詳細統計數據
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  位置
                </th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  描述
                </th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: 600 }}>
                  範例
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  最小值 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  Q1 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  中位數 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  Q3 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  最大值 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  平均值 (s)
                </th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>
                  樣本數
                </th>
              </tr>
            </thead>
            <tbody>
              {positionData.map((row, idx) => (
                <tr 
                  key={idx}
                  style={{ 
                    borderBottom: '1px solid var(--border-color)',
                    transition: 'background 0.2s',
                    background: idx % 2 === 0 ? 'var(--bg-secondary)' : 'transparent'
                  }}
                >
                  <td style={{ padding: '12px', color: 'var(--text-primary)', fontWeight: 600 }}>
                    {row.position}
                  </td>
                  <td style={{ padding: '12px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {row.description}
                  </td>
                  <td style={{ padding: '12px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                    {row.example}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#00ccff' }}>
                    {row.min.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#8884d8' }}>
                    {row.q1.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#ffd700', fontWeight: 600 }}>
                    {row.med.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#82ca9d' }}>
                    {row.q3.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#ff6b6b' }}>
                    {row.max.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#00ff88', fontWeight: 600 }}>
                    {row.mean.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)' }}>
                    n={row.n}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 關鍵發現 */}
      <div className="card">
        <div className="card-title">
          <Info size={20} />
          關鍵發現
        </div>
        <div className="findings-list">
          <div className="finding-item">
            <div className="finding-icon">📊</div>
            <div className="finding-content">
              <div className="finding-title">平均破解時間差異適中</div>
              <div className="finding-desc">三種位置的平均破解時間分別為 Prefix (206.84s), Suffix (193.67s), Mixed (267.50s)，Mixed 位置相對最慢約 38% (相對 Suffix)</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">📈</div>
            <div className="finding-content">
              <div className="finding-title">中位數顯示更明顯差異</div>
              <div className="finding-desc">Mixed 位置的中位數 (40.99s) 是 Suffix (21.75s) 的約 1.9 倍，顯示特殊字符分散確實增加破解難度</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🎯</div>
            <div className="finding-content">
              <div className="finding-title">離散度差異顯著</div>
              <div className="finding-desc">Mixed 的 Q3 (241.52s) 遠高於 Prefix (79.89s) 和 Suffix (63.03s)，表示分散放置特殊字符使破解時間更不可預測</div>
            </div>
          </div>
          <div className="finding-item">
            <div className="finding-icon">🔒</div>
            <div className="finding-content">
              <div className="finding-title">安全建議：分散放置特殊字符</div>
              <div className="finding-desc">雖然位置影響相對其他因素較小，但 Mixed 模式的中位數和平均值均較高，建議將特殊字符分散在密碼中以提升安全性</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Summary() {
  const chartHeight = useResponsiveHeight(450);
  
  const recommendations = [
    {
      level: '🟢 安全',
      length: '12+ 字符',
      time: '數年以上',
      description: '混合大小寫、數字、特殊字符，高度安全',
      color: 'success'
    },
    {
      level: '🟡 中等',
      length: '10-11 字符',
      time: '數週至數月',
      description: '含 2-3 種字符類型，中等安全',
      color: 'info'
    },
    {
      level: '🔴 危險',
      length: '8-9 字符',
      time: '數分鐘至數小時',
      description: '即使混合字符也較容易被破解',
      color: 'warning'
    }
  ];

  const bestPractices = [
    {
      icon: '📏',
      title: '長度優先',
      description: '密碼長度是最重要的安全因素，建議至少 12 字符'
    },
    {
      icon: '🎨',
      title: '多樣化字符',
      description: '混合大小寫、數字和特殊字符，增加搜索空間'
    },
    {
      icon: '🔄',
      title: '定期更換',
      description: '定期更新密碼，降低長期暴露風險'
    },
    {
      icon: '🔐',
      title: '使用密碼管理器',
      description: '生成和管理複雜的隨機密碼'
    }
  ];

  const keyFindings = [
    {
      title: '長度指數增長',
      stat: '45萬×',
      description: '密碼從 8 增加到 12 字符，破解時間增長超過 45 萬倍'
    },
    {
      title: '特殊字符效果',
      stat: '70×',
      description: '增加 1-4 個特殊字符可使破解時間增長約 70 倍'
    },
    {
      title: '字符多樣性',
      stat: '36×',
      description: '從單一字符類型到多種類型，破解時間增長 36 倍'
    },
    {
      title: '位置影響有限',
      stat: '~7%',
      description: '特殊字符位置差異僅約 7%，影響相對較小'
    }
  ];

  return (
    <div className="summary">
      <div className="key-stats-grid">
        {keyFindings.map((finding, index) => (
          <div key={index} className="key-stat-card">
            <div className="stat-number">{finding.stat}</div>
            <div className="stat-title">{finding.title}</div>
            <div className="stat-desc">{finding.description}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-title">
          <CheckCircle size={20} />
          密碼安全等級建議
        </div>
        <div className="recommendations-list">
          {recommendations.map((rec, index) => (
            <div key={index} className={`recommendation-card level-${rec.color}`}>
              <div className="rec-header">
                <div className="rec-level">{rec.level}</div>
                <div className="rec-badge">{rec.length}</div>
              </div>
              <div className="rec-time">預估破解時間: {rec.time}</div>
              <div className="rec-desc">{rec.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <Info size={20} />
          密碼安全最佳實踐
        </div>
        <div className="best-practices-grid">
          {bestPractices.map((practice, index) => (
            <div key={index} className="practice-card">
              <div className="practice-icon">{practice.icon}</div>
              <div className="practice-title">{practice.title}</div>
              <div className="practice-desc">{practice.description}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card conclusion-card">
        <div className="card-title">
          <TrendingUp size={20} />
          實驗結論
        </div>
        <div className="conclusion-content">
          <p className="conclusion-intro">
            通過兩輪系統性實驗（Round 1 和 Round 2），我們使用 Mask Attack 模式量化分析了影響密碼破解時間的四個關鍵因素：
          </p>
          <div className="conclusion-points">
            <div className="point">
              <strong>1. 密碼長度影響（Round 1 - Firsttest）</strong>
              <p>密碼長度是最關鍵的安全因素。從 8 位增加到 12 位，破解時間從 11.2 秒增加到 5,116,514 秒（約 59 天），增長超過 45 萬倍。每增加一個字符的邊際時間成本呈指數增長。</p>
            </div>
            <div className="point">
              <strong>2. 特殊字符數量影響（Round 1 - Secondtest）</strong>
              <p>在 8 字符基礎上增加 1-4 個特殊字符，破解時間從 45.8 秒增加到 3229.7 秒，增長約 70 倍。每增加一個特殊字符的邊際成本遞增，顯示性價比最高的配置是 2-3 個特殊字符。</p>
            </div>
            <div className="point">
              <strong>3. 字符種類多樣性（Round 2 - Firsttest）</strong>
              <p>字符類型從單一類型（Level 1）增加到多種類型（Level 3），破解時間從 12.5 秒增加到 456.7 秒，增長約 36 倍。字符集大小（26 → 95）直接影響搜索空間。</p>
            </div>
            <div className="point">
              <strong>4. 特殊字符位置影響（Round 2 - Secondtest）</strong>
              <p>特殊字符位於前綴、後綴或混合位置的破解時間差異僅約 7%（85.4 - 91.7 秒），顯示在 Mask Attack 模式下，位置影響相對有限。重要的是特殊字符的存在而非位置。</p>
            </div>
          </div>
          <div className="final-recommendation">
            <strong>最終建議：</strong>
            基於實驗數據，最安全的密碼策略是：使用至少 12 位長度、混合 3-4 種字符類型（小寫+大寫+數字+特殊字符）、包含 2-3 個特殊字符的隨機密碼。
            這樣的密碼在面對 Mask Attack 時，破解時間將達到數週甚至數年級別，提供充分的安全保障。
            建議使用密碼管理器生成和管理此類複雜密碼。
          </div>
        </div>
      </div>
    </div>
  );
}

export default Results
