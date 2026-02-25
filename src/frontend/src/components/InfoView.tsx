// src/frontend/src/components/InfoView.tsx
import React, { useMemo, useState } from 'react';
import '../styles/MenuScreens.css';
import '../styles/InboxView.css';
import { infoSections, InfoRule } from '../content/infoData';

type Props = {
  onBack: () => void;
  onOpenMenu: () => void;
};

const InfoView: React.FC<Props> = ({ onBack, onOpenMenu }) => {
  const [openRuleIds, setOpenRuleIds] = useState<Set<string>>(new Set());

  const allRules = useMemo(() => {
    const out: InfoRule[] = [];
    infoSections.forEach((s) => s.rules.forEach((r) => out.push(r)));
    return out;
  }, []);

  const toggleRule = (id: string) => {
    setOpenRuleIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const expandAll = () => setOpenRuleIds(new Set(allRules.map((r) => r.id)));
  const collapseAll = () => setOpenRuleIds(new Set());

  return (
    <div className="outlook-shell">
      <div className="outlook-topbar">
        <div className="outlook-topbar-left">
          <button className="btn" onClick={onBack}>
            Back
          </button>
          <div className="outlook-topbar-title">Info & tutorial</div>
        </div>

        <div className="outlook-topbar-actions">
          <button className="btn" onClick={expandAll} title="Expand all sections">
            Expand all
          </button>
          <button className="btn" onClick={collapseAll} title="Collapse all sections">
            Collapse all
          </button>

          <button
            className="hamburger-btn"
            onClick={onOpenMenu}
            aria-label="Open menu"
            title="Menu"
          >
            ☰
          </button>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '280px 1fr',
          gap: 14,
          padding: 14,
          overflow: 'hidden',
          flex: 1,
        }}
      >
        {/* TOC */}
        <div
          style={{
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: 12,
            padding: 12,
            overflow: 'auto',
            maxHeight: 'calc(100vh - 140px)',
          }}
        >
          <div style={{ fontWeight: 800, marginBottom: 8 }}>Contents</div>
          <div style={{ display: 'grid', gap: 8 }}>
            {infoSections.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                className="link-like"
                style={{
                  display: 'block',
                  textAlign: 'left',
                  padding: '6px 8px',
                  borderRadius: 8,
                  textDecoration: 'none',
                }}
              >
                {s.title}
              </a>
            ))}
          </div>

          <div style={{ marginTop: 12, fontSize: 12, opacity: 0.8 }}>
            Info: this page is designed to be reused for feedback hints in the game, so sections are written as
            small “rules”.
          </div>
        </div>

        {/* Main content */}
        <div
          style={{
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: 12,
            padding: 14,
            overflow: 'auto',
            maxHeight: 'calc(100vh - 140px)',
          }}
        >
          {infoSections.map((section) => (
            <div key={section.id} id={section.id} style={{ marginBottom: 22 }}>
              <h2 style={{ margin: '6px 0 6px' }}>{section.title}</h2>
              <div style={{ opacity: 0.9, marginBottom: 10 }}>{section.intro}</div>

              <div style={{ display: 'grid', gap: 10 }}>
                {section.rules.map((rule) => {
                  const open = openRuleIds.has(rule.id);

                  return (
                    <div
                      key={rule.id}
                      style={{
                        border: '1px solid rgba(255,255,255,0.12)',
                        borderRadius: 12,
                        padding: 12,
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => toggleRule(rule.id)}
                        className="btn"
                        style={{
                          width: '100%',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          gap: 10,
                        }}
                        aria-expanded={open}
                        aria-controls={`rule-${rule.id}`}
                      >
                        <span style={{ fontWeight: 800, textAlign: 'left' }}>{rule.title}</span>
                        <span style={{ opacity: 0.75 }}>{open ? '–' : '+'}</span>
                      </button>

                      <div
                        id={`rule-${rule.id}`}
                        style={{
                          marginTop: 10,
                          display: open ? 'block' : 'none',
                        }}
                      >
                        <div style={{ fontSize: 14, opacity: 0.95, marginBottom: 8 }}>
                          {rule.summary}
                        </div>

                        <ul style={{ margin: 0, paddingLeft: 18 }}>
                          {rule.details.map((d, i) => (
                            <li key={i} style={{ marginBottom: 6, lineHeight: 1.35 }}>
                              {d}
                            </li>
                          ))}
                        </ul>

                        {rule.examples && rule.examples.length > 0 && (
                          <div style={{ marginTop: 10 }}>
                            <div style={{ fontWeight: 800, marginBottom: 6 }}>Examples</div>
                            <ul style={{ margin: 0, paddingLeft: 18, opacity: 0.95 }}>
                              {rule.examples.map((ex, i) => (
                                <li key={i} style={{ marginBottom: 6, lineHeight: 1.35 }}>
                                  {ex}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <div style={{ marginTop: 10, fontSize: 12, opacity: 0.7 }}>
                          Tags: {rule.tags.join(', ')}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          <div style={{ marginTop: 20, fontSize: 12, opacity: 0.75 }}>
            Reminder: if an email pressures you to move quickly, that is usually the moment you should slow
            down and verify.
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoView;