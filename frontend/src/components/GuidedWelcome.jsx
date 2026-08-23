import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function GuidedWelcome({ suggestions, onSelectCategory }) {
  if (!suggestions) return null;

  return (
    <div className="welcome-hero">
      <div className="welcome-title">
        Hello 👋 Welcome to DDU AI Assistant
      </div>
      <div className="welcome-desc">
        Ask anything about Dharmsinh Desai University (Nadiad) — admissions, 75% attendance rule, fees, scholarships (MYSY), SPI/CPI calculation, campus placements, hostels, or circulars. Or choose a quick topic below:
      </div>

      <div className="guided-categories-grid">
        {suggestions.primary_categories?.map((cat) => (
          <div
            key={cat.id}
            className="category-card"
            onClick={() => onSelectCategory(cat.id)}
          >
            <div className="category-icon">{cat.icon}</div>
            <div>
              <div className="category-name">{cat.name}</div>
              <div className="category-subtext">{cat.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
