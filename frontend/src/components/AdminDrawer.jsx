import React, { useState, useRef } from 'react';
import { UploadCloud, RefreshCw, Globe, Trash2, CheckCircle2, AlertCircle, FileText, Layers } from 'lucide-react';
import { apiService } from '../services/api';

export default function AdminDrawer({ stats, onRefreshStats }) {
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [message, setMessage] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);
    try {
      const res = await apiService.uploadDocument(file);
      setMessage({ type: 'success', text: res.message || 'Document uploaded and indexed successfully!' });
      onRefreshStats();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm(`Are you sure you want to delete document ${docId}? It will be purged from ChromaDB.`)) return;

    try {
      await apiService.deleteDocument(docId);
      setMessage({ type: 'success', text: `Document ${docId} deleted and purged from ChromaDB.` });
      onRefreshStats();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setMessage(null);
    try {
      const res = await apiService.triggerReindex();
      setMessage({ type: 'success', text: 'ChromaDB index rebuilt successfully!' });
      onRefreshStats();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setReindexing(false);
    }
  };

  const handleScrape = async () => {
    setScraping(true);
    setMessage(null);
    try {
      const res = await apiService.triggerLiveScrape();
      setMessage({ type: 'success', text: `Scraped ${res.details?.scrape_stats?.pages_scraped || 0} pages and updated vector store!` });
      onRefreshStats();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="admin-hub-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Knowledge Base & Document Ingestion Management
          </h2>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Manage university knowledge streams, upload official PDFs/notices, and sync ChromaDB.
          </div>
        </div>

        <div className="admin-actions-bar">
          <button className="btn-secondary" onClick={handleScrape} disabled={scraping}>
            <Globe size={15} />
            <span>{scraping ? 'Scraping ddu.ac.in...' : 'Scrape Website'}</span>
          </button>

          <button className="btn-primary" onClick={handleReindex} disabled={reindexing}>
            <RefreshCw size={15} className={reindexing ? 'spin' : ''} />
            <span>{reindexing ? 'Rebuilding Index...' : 'Re-index All'}</span>
          </button>
        </div>
      </div>

      {message && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: message.type === 'success' ? 'rgba(13, 148, 136, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: message.type === 'success' ? 'var(--ddu-teal)' : '#ef4444',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.88rem',
          fontWeight: 600
        }}>
          {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* KPI Overview */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-label">Total Vector Chunks</div>
          <div className="stat-number">{stats?.total_chunks || 0}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Indexed in ChromaDB</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Active Knowledge Documents</div>
          <div className="stat-number">{stats?.total_documents || 0}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDFs, Policies, Text files</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Covered Categories</div>
          <div className="stat-number" style={{ color: 'var(--ddu-gold)' }}>
            {Object.keys(stats?.categories || {}).length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Admissions, Attendance, etc.</div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="dropzone-box" onClick={() => fileInputRef.current?.click()}>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept=".pdf,.txt,.md"
          onChange={handleFileUpload}
        />
        <UploadCloud size={40} color="var(--ddu-blue)" style={{ margin: '0 auto 0.5rem auto' }} />
        <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          {uploading ? 'Processing & Embedding Document...' : 'Click to Upload Official DDU Document (PDF / TXT / MD)'}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Automatically parsed, chunked, and embedded into ChromaDB with metadata.
        </div>
      </div>

      {/* Documents Repository Table */}
      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <FileText size={18} color="var(--ddu-blue)" /> Indexed Knowledge Documents
        </h3>
        <table className="recruiters-table">
          <thead>
            <tr>
              <th>Document Name</th>
              <th>Category</th>
              <th>Format</th>
              <th>Vector Chunks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {stats?.documents && stats.documents.length > 0 ? (
              stats.documents.map((doc, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>📄 {doc.source}</td>
                  <td>
                    <span className="badge-tag">{doc.category}</span>
                  </td>
                  <td style={{ textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 600 }}>
                    {doc.file_type}
                  </td>
                  <td style={{ fontWeight: 600 }}>{doc.chunk_count} chunks</td>
                  <td>
                    <button className="btn-delete" onClick={() => handleDelete(doc.doc_id)} title="Delete document & purge chunks">
                      <Trash2 size={13} style={{ display: 'inline', marginRight: '3px' }} /> Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '1.5rem' }}>
                  No documents found in knowledge base. Click "Re-index All" or upload a file.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
