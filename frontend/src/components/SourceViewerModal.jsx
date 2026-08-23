import React from 'react';
import { X, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function SourceViewerModal({ citation, onClose }) {
  if (!citation) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText className="text-ddu-blue" size={20} color="var(--ddu-blue)" />
            <div className="modal-title">{citation.source}</div>
          </div>
          <button className="icon-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span className="badge-tag">Category: {citation.category}</span>
          <span className="badge-tag">Page / Section: {citation.page || 1}</span>
          <span className="badge-tag" style={{ background: 'rgba(13, 148, 136, 0.1)', color: 'var(--ddu-teal)' }}>
            <ShieldCheck size={12} style={{ display: 'inline', marginRight: '3px' }} />
            Match Confidence: {Math.round(citation.similarity_score * 100)}%
          </span>
        </div>

        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
            VERIFIED EXTRACTED TEXT CHUNK:
          </div>
          <div className="snippet-box">
            {citation.snippet}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn-secondary" onClick={onClose}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
