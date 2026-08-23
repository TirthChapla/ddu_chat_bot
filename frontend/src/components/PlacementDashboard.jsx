import React, { useEffect, useState } from 'react';
import { Award, Briefcase, TrendingUp, Building, CheckCircle, Info } from 'lucide-react';
import { apiService } from '../services/api';

export default function PlacementDashboard({ onAskQuery }) {
  const [placementData, setPlacementData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.fetchPlacementAnalytics()
      .then(data => {
        setPlacementData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="dashboard-view" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="typing-indicator">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            DDU Training & Placement (T&P) Analytics
          </h2>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Official recruitment statistics, top hiring companies, and branch placement rates.
          </div>
        </div>

        <button
          className="btn-primary"
          onClick={() => onAskQuery("What are the placement eligibility rules, average package, and top recruiters at DDU?")}
        >
          <span>Ask Bot About Placements</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-label">Highest Package</div>
          <div className="stat-number">{placementData?.highest_package || '₹44.0 LPA'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Amazon / Microsoft / Off-campus</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">IT & CE Average CTC</div>
          <div className="stat-number">{placementData?.average_it_ce || '₹8.5 LPA'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Software Engineering & Cloud</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Overall University Average</div>
          <div className="stat-number">{placementData?.average_overall || '₹6.5 LPA'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>All Engineering & Tech Branches</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Placement Conversion Rate</div>
          <div className="stat-number" style={{ color: 'var(--ddu-teal)' }}>{placementData?.placement_rate || '92%'}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Eligible registered students</div>
        </div>
      </div>

      {/* Branch Breakdown Table */}
      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <TrendingUp size={18} color="var(--ddu-blue)" /> Branch-wise Placement & Average Package
        </h3>
        <table className="recruiters-table">
          <thead>
            <tr>
              <th>Branch / Department</th>
              <th>Placed Percentage</th>
              <th>Average Package (CTC)</th>
              <th>Key Sectors</th>
            </tr>
          </thead>
          <tbody>
            {placementData?.branch_distribution?.map((item, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 600 }}>{item.branch}</td>
                <td>
                  <span style={{ color: 'var(--ddu-teal)', fontWeight: 700 }}>{item.placed_pct}%</span>
                </td>
                <td style={{ fontWeight: 600 }}>₹{item.avg_lpa} LPA</td>
                <td style={{ color: 'var(--text-secondary)' }}>Software, Fintech, Core & Consulting</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Prominent Recruiters */}
      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Building size={18} color="var(--ddu-blue)" /> Top Recruiting Partners
        </h3>
        <table className="recruiters-table">
          <thead>
            <tr>
              <th>Company Name</th>
              <th>Industry / Sector</th>
              <th>Offer Tier</th>
              <th>Typical CTC Range</th>
            </tr>
          </thead>
          <tbody>
            {placementData?.top_recruiters?.map((rec, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 700 }}>{rec.name}</td>
                <td>{rec.type}</td>
                <td>
                  <span className="badge-tag">{rec.tier}</span>
                </td>
                <td style={{ fontWeight: 600 }}>{rec.avg_ctc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
