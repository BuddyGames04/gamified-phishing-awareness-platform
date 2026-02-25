import React, { useEffect, useState } from 'react';
import { fetchPvpMyLevels, publishPvpLevel, PvpLevel } from '../../api';

type Props = {
  onBack?: () => void;
  onPlay: (levelId: number) => void;
  showBack?: boolean;
};

const PvpMyLevels: React.FC<Props> = ({ onBack, onPlay, showBack = true }) => {
  const [levels, setLevels] = useState<PvpLevel[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const refresh = () => {
    fetchPvpMyLevels()
      .then(setLevels)
      .catch((e) => setErr(String(e)));
  };

  useEffect(() => {
    refresh();
  }, []);

  const onPublish = async (id: number) => {
    setBusyId(id);
    setErr(null);
    try {
      await publishPvpLevel(id);
      refresh();
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div style={{ padding: 18, maxWidth: 1000, margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h2 style={{ margin: 0 }}>My Levels</h2>
        {showBack && onBack && (
          <button className="btn" onClick={onBack}>
            Back
          </button>
        )}
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
              <div style={{ fontWeight: 700 }}>
                {lvl.title}{' '}
                <span style={{ fontSize: 12, opacity: 0.7 }}>({lvl.visibility})</span>
              </div>
              <div style={{ fontSize: 13, opacity: 0.85 }}>
                {lvl.scenario?.company_name} — {lvl.scenario?.role_title}
              </div>
              <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
                Created: {new Date(lvl.created_at).toLocaleString()}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-ok" onClick={() => onPlay(lvl.id)}>
                Play
              </button>
              {lvl.visibility !== 'posted' && (
                <button
                  className="btn btn-danger"
                  disabled={busyId === lvl.id}
                  onClick={() => onPublish(lvl.id)}
                >
                  {busyId === lvl.id ? 'Publishing…' : 'Publish'}
                </button>
              )}
            </div>
          </div>
        ))}

        {levels.length === 0 && !err && (
          <div style={{ opacity: 0.8 }}>You haven’t created any levels yet.</div>
        )}
      </div>
    </div>
  );
};

export default PvpMyLevels;
