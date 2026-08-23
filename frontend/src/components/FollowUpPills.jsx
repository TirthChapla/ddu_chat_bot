import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function FollowUpPills({ followUps, onSelectFollowUp }) {
  if (!followUps || followUps.length === 0) return null;

  return (
    <div style={{ marginTop: '0.4rem' }}>
      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
        <HelpCircle size={12} />
        <span>Suggested follow-up questions:</span>
      </div>
      <div className="followups-group">
        {followUps.map((text, idx) => (
          <button
            key={idx}
            className="followup-pill"
            onClick={() => onSelectFollowUp(text)}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}
