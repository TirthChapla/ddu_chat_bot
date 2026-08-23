import React from 'react';
import ReactMarkdown from 'react-markdown';
import FollowUpPills from './FollowUpPills';

export default function MessageBubble({ message, onSelectFollowUp, isLast }) {
  const isBot = message.role === 'assistant';

  return (
    <div className={`message-row ${isBot ? 'bot' : 'user'}`}>
      <div className={`message-avatar ${isBot ? 'bot' : 'user'}`}>
        {isBot ? '🎓' : '👤'}
      </div>

      <div className="message-content-wrapper">
        <div className={`message-bubble ${isBot ? 'bot' : 'user'}`}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Dynamic Follow-Up Suggestions on Latest Message */}
        {isBot && isLast && message.follow_up_suggestions && (
          <FollowUpPills
            followUps={message.follow_up_suggestions}
            onSelectFollowUp={onSelectFollowUp}
          />
        )}
      </div>
    </div>
  );
}
