import React from 'react';
import { MessageSquare, BarChart2, Sun, Moon, ArrowLeft, Shield } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, theme, toggleTheme, stats, isAdminRoute, onNavigate }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="logo-badge">🎓</div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="brand-title">DDU AI Assistant</span>
            {isAdminRoute && (
              <span className="badge-tag" style={{ background: 'rgba(217, 119, 6, 0.15)', color: 'var(--ddu-gold)', border: '1px solid rgba(217, 119, 6, 0.3)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                <Shield size={11} /> Admin Hub
              </span>
            )}
          </div>
          <div className="brand-subtitle">Dharmsinh Desai University, Nadiad</div>
        </div>
      </div>

      {/* Regular Student Navigation: Only AI Chat & Placement Hub */}
      {!isAdminRoute ? (
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={15} />
            <span>AI Chat</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'placements' ? 'active' : ''}`}
            onClick={() => setActiveTab('placements')}
          >
            <BarChart2 size={15} />
            <span>Placement Hub</span>
          </button>
        </nav>
      ) : (
        /* Admin Navigation */
        <nav className="nav-tabs">
          <button
            className="nav-tab-btn"
            onClick={() => onNavigate('/')}
            title="Return to Student AI Assistant"
            style={{ color: 'var(--ddu-blue)' }}
          >
            <ArrowLeft size={15} />
            <span>Back to Student Chat</span>
          </button>
        </nav>
      )}

      <div className="header-actions">
        <div className="status-pill" title="ChromaDB RAG Engine Active">
          <span className="status-dot"></span>
          <span>RAG Online ({stats?.total_chunks || 'Ready'})</span>
        </div>

        <button 
          className="icon-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
        </button>
      </div>
    </header>
  );
}
