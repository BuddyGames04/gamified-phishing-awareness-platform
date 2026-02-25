import React, { useEffect, useState } from 'react';
import { fetchPvpPostedLevels, PvpLevel } from '../../api';

type Props = {
  onBack: () => void;
  onPlay: (levelId: number) => void;
};

const PvpBrowsePosted: React.FC<Props> = ({ onBack, onPlay }) => {
  const [levels, setLevels] = useState<PvpLevel[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchPvpPostedLevels()
      .then(setLevels)
      .catch((e) => setErr(String(e)));
  }, []);

  return (
    <div style={{ padding: 18, maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Posted Levels</h2>
        <button className="btn" onClick={onBack}>Back</button>
      </div>

      {err && <div style={{ marginTop: 12, color: 'salmon' }}>{err}</div>}

      <div style={{ marginTop: 16, display: 'grid', gap: 10 }}>
        {levels.map((lvl) => (
          <div
            key={lvl.id}
            style={{
              border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: 10,
              padding: 12,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <div>
              <div style={{ fontWeight: 700 }}>{lvl.title}</div>
              <div style={{ fontSize: 13, opacity: 0.85 }}>
                {lvl.scenario?.company_name} — {lvl.scenario?.role_title}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
                Plays: {lvl.plays} • Avg accuracy: {Math.round((lvl.avg_accuracy || 0) * 100)}%
              </div>
            </div>

            <button className="btn btn-ok" onClick={() => onPlay(lvl.id)}>
              Play
            </button>
          </div>
        ))}
        {levels.length === 0 && !err && (
          <div style={{ opacity: 0.8 }}>No posted levels yet.</div>
        )}
      </div>
    </div>
  );
};

export default PvpBrowsePosted;