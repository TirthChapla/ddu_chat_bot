import React from 'react';
import { X, Sparkles } from 'lucide-react';

export default function SubTopicGrid({ categoryId, subtopics, onSelectTopic, onClose }) {
  if (!categoryId || !subtopics || subtopics.length === 0) return null;

  const categoryName = categoryId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <div className="subtopic-banner">
      <div className="subtopic-header">
        <div className="subtopic-title">
          <Sparkles size={14} />
          <span>Quick actions for <strong>{categoryName}</strong>:</span>
        </div>
        <button
          className="icon-btn"
          style={{ width: '24px', height: '24px' }}
          onClick={onClose}
          title="Close subtopics"
        >
          <X size={13} />
        </button>
      </div>

      <div className="subtopics-chips">
        {subtopics.map((topic, idx) => (
          <button
            key={idx}
            className="subtopic-chip"
            onClick={() => onSelectTopic(topic.query)}
          >
            👉 {topic.label}
          </button>
        ))}
      </div>
    </div>
  );
}
