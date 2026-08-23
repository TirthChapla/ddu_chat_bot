import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import PlacementDashboard from './components/PlacementDashboard';
import AdminDrawer from './components/AdminDrawer';
import SourceViewerModal from './components/SourceViewerModal';
import { apiService } from './services/api';

export default function App() {
  // Route state: synchronized with URL pathname
  const [currentPath, setCurrentPath] = useState(() => window.location.pathname);
  const [activeTab, setActiveTab] = useState('chat');
  const [theme, setTheme] = useState(() => localStorage.getItem('ddu_theme') || 'dark');
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeCitation, setActiveCitation] = useState(null);

  // Sync with browser navigation (Back / Forward / URL change)
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  const isAdminRoute = currentPath === '/admin' || currentPath.startsWith('/admin');

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ddu_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Load initial suggestions and stats
  const refreshStats = () => {
    apiService.fetchAdminStats().then(setStats).catch(console.error);
  };

  useEffect(() => {
    apiService.fetchSuggestions().then(setSuggestions).catch(console.error);
    refreshStats();
  }, []);

  const handleSendMessage = async (queryText, category = null) => {
    const userMsg = { role: 'user', content: queryText };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      // Build brief history format
      const historyPayload = messages.slice(-4).map(m => ({ role: m.role, content: m.content }));
      const response = await apiService.sendChatMessage(queryText, category, historyPayload);

      const botMsg = {
        role: 'assistant',
        content: response.answer,
        category: response.category,
        sources: response.sources || [],
        follow_up_suggestions: response.follow_up_suggestions || [],
        latency_ms: response.latency_ms,
        confidence: response.confidence
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ **Error retrieving information:** ${err.message}. Please check if the backend server is running.`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleAskQueryFromPlacement = (query) => {
    setActiveTab('chat');
    handleSendMessage(query);
  };

  return (
    <div className="app-layout">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        theme={theme}
        toggleTheme={toggleTheme}
        stats={stats}
        isAdminRoute={isAdminRoute}
        onNavigate={navigate}
      />

      <main className="main-view-container">
        {isAdminRoute ? (
          /* Dedicated Admin Route: http://localhost:5173/admin */
          <AdminDrawer stats={stats} onRefreshStats={refreshStats} />
        ) : (
          /* Student Portal: http://localhost:5173/ */
          <>
            {activeTab === 'chat' && (
              <ChatContainer
                messages={messages}
                suggestions={suggestions}
                loading={loading}
                onSendMessage={handleSendMessage}
                onClearChat={handleClearChat}
                onOpenCitation={setActiveCitation}
              />
            )}

            {activeTab === 'placements' && (
              <PlacementDashboard onAskQuery={handleAskQueryFromPlacement} />
            )}
          </>
        )}
      </main>

      {/* Source Citation Modal */}
      {activeCitation && (
        <SourceViewerModal
          citation={activeCitation}
          onClose={() => setActiveCitation(null)}
        />
      )}
    </div>
  );
}
