import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Activity, Database, FileText, BarChart3, Menu, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ExperimentDesign from './pages/ExperimentDesign'
import Results from './pages/Results'
import './App.css'

function App() {
  // 根據屏幕大小設置側邊欄初始狀態
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    return window.innerWidth > 768
  })

  // 監聽屏幕大小變化
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setSidebarOpen(false)
      }
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <Router>
      <div className={`app ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <Sidebar 
          isOpen={sidebarOpen} 
          setIsOpen={setSidebarOpen} 
        />
        {/* 移動端點擊遮罩關閉側邊欄 (只在平板和手機模式下顯示) */}
        {sidebarOpen && window.innerWidth <= 768 && (
          <div 
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        <main className={`main-content ${sidebarOpen ? 'shifted' : ''}`}>
          <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
          <div className="content-wrapper">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/design" element={<ExperimentDesign />} />
              <Route path="/results" element={<Results />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Activity, label: '儀表板' },
    { path: '/design', icon: FileText, label: '實驗設計' },
    { path: '/results', icon: BarChart3, label: '數據結果' },
  ]

  // 在移動端點擊導航項後自動關閉側邊欄
  const handleNavClick = () => {
    if (window.innerWidth <= 768) {
      setIsOpen(false)
    }
  }

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <Database className="logo-icon" />
        {isOpen && <h1 className="logo-text">Hashcat 實驗</h1>}
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
              title={item.label}
              onClick={handleNavClick}
            >
              <Icon size={20} />
              {isOpen && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        {isOpen && (
          <div className="footer-text">
            <p>密碼破解效能分析</p>
            <p className="version">v1.0.0</p>
          </div>
        )}
      </div>
    </aside>
  )
}

function Header({ toggleSidebar }) {
  const location = useLocation()

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return '儀表板總覽'
      case '/design':
        return '實驗設計'
      case '/results':
        return '數據結果分析'
      default:
        return 'Hashcat 實驗'
    }
  }

  return (
    <header className="header">
      <div className="header-left">
        <button className="menu-btn" onClick={toggleSidebar}>
          <Menu size={24} />
        </button>
        <h2 className="page-title">{getPageTitle()}</h2>
      </div>
      
      <div className="header-right">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>系統運行中</span>
        </div>
      </div>
    </header>
  )
}

export default App
