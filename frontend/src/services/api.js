/**
 * API Service for DDU AI Assistant Backend
 */

const API_BASE = '/api';

export const apiService = {
  // Chat & RAG
  async sendChatMessage(query, category = null, history = []) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, category, history })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to get answer from assistant');
    }
    return res.json();
  },

  // Suggestions & Guided Taxonomy
  async fetchSuggestions() {
    const res = await fetch(`${API_BASE}/suggestions`);
    if (!res.ok) throw new Error('Failed to load guided suggestions');
    return res.json();
  },

  // Admin Knowledge Base Stats
  async fetchAdminStats() {
    const res = await fetch(`${API_BASE}/admin/stats`);
    if (!res.ok) throw new Error('Failed to fetch knowledge base statistics');
    return res.json();
  },

  // Upload Document (PDF/TXT)
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/admin/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  // Delete Document
  async deleteDocument(docId) {
    const res = await fetch(`${API_BASE}/admin/documents/${docId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  // Re-index ChromaDB
  async triggerReindex() {
    const res = await fetch(`${API_BASE}/admin/reindex`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger re-index');
    return res.json();
  },

  // Trigger Web Scrape
  async triggerLiveScrape() {
    const res = await fetch(`${API_BASE}/admin/scrape`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to scrape DDU portal');
    return res.json();
  },

  // Placement Analytics
  async fetchPlacementAnalytics() {
    const res = await fetch(`${API_BASE}/analytics/placements`);
    if (!res.ok) throw new Error('Failed to fetch placement data');
    return res.json();
  },

  // Query Logs
  async fetchQueryLogs() {
    const res = await fetch(`${API_BASE}/analytics/queries`);
    if (!res.ok) throw new Error('Failed to fetch query logs');
    return res.json();
  }
};
