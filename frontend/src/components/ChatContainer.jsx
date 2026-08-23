import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Trash2 } from 'lucide-react';
import GuidedWelcome from './GuidedWelcome';
import SubTopicGrid from './SubTopicGrid';
import MessageBubble from './MessageBubble';

export default function ChatContainer({
  messages,
  suggestions,
  loading,
  onSendMessage,
  onClearChat,
  onOpenCitation
}) {
  const [inputText, setInputText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || loading) return;
    onSendMessage(inputText.trim());
    setInputText('');
    setSelectedCategory(null);
  };

  const handleSelectCategory = (catId) => {
    setSelectedCategory(catId);
  };

  const handleSelectSubTopic = (query) => {
    onSendMessage(query, selectedCategory);
    setSelectedCategory(null);
  };

  const handleSelectFollowUp = (query) => {
    onSendMessage(query);
  };

  return (
    <div className="chat-section">
      <div className="messages-scroll-area">
        {/* Empty state: Guided Welcome */}
        {messages.length === 0 && (
          <GuidedWelcome
            suggestions={suggestions}
            onSelectCategory={handleSelectCategory}
          />
        )}

        {/* Guided Category Drilldown Subtopics */}
        {selectedCategory && suggestions?.sub_topics?.[selectedCategory] && (
          <SubTopicGrid
            categoryId={selectedCategory}
            subtopics={suggestions.sub_topics[selectedCategory]}
            onSelectTopic={handleSelectSubTopic}
            onClose={() => setSelectedCategory(null)}
          />
        )}

        {/* Message Thread */}
        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            message={msg}
            onSelectFollowUp={handleSelectFollowUp}
            isLast={idx === messages.length - 1}
          />
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="message-row bot">
            <div className="message-avatar bot">🎓</div>
            <div className="message-bubble bot" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Consulting DDU Knowledge Base & Vector Index...
              </span>
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="chat-input-wrapper">
        <form onSubmit={handleSubmit} className="input-box-container">
          <input
            type="text"
            className="chat-text-input"
            placeholder="Ask about admissions, 75% attendance rule, fees, placements, exams..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
          />
          {messages.length > 0 && (
            <button
              type="button"
              className="icon-btn"
              style={{ width: '34px', height: '34px' }}
              onClick={onClearChat}
              title="Clear conversation"
            >
              <Trash2 size={14} />
            </button>
          )}
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!inputText.trim() || loading}
            title="Send Query"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
