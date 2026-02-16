import React, { useEffect, useState } from 'react';
import { fetchProfileMetrics, ProfileMetrics } from '../api';
import '../styles/ProfileView.css';

type Props = { userId: string };

function asPercent(v: number) {
  // supports either 0..1 or 0..100
  if (!Number.isFinite(v)) return 0;
  return v <= 1 ? v * 100 : v;
}

const ProfileView: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<ProfileMetrics | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;

    (async () => {
      setLoading(true);
      setErr(null);
      try {
        const d = await fetchProfileMetrics(userId);
        if (alive) setData(d);
      } catch (e: any) {
        if (alive) setErr(e?.message || 'Failed to load metrics');
      } finally {
        if (alive) setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, [userId]);

  if (loading) return <div className="profile-shell">Loading metrics…</div>;
  if (err) return <div className="profile-shell">Error: {err}</div>;
  if (!data) return <div className="profile-shell">No metrics found.</div>;

  const overallAccuracyPct = asPercent(data.overall.accuracy);
  const linkBeforePct = asPercent(data.overall.pct_link_click_before_decision);
  const attachBeforePct = asPercent(data.overall.pct_attachment_open_before_decision);

  return (
    <div className="profile-shell">
      <h2 className="profile-title">Your Profile</h2>
      <div className="profile-subtitle">
        User: <strong>{data.user_id}</strong>
      </div>

      <div className="profile-grid">
        <div className="profile-card">
          <div className="profile-card-title">Overall performance</div>
          <div className="profile-big">{Math.round(overallAccuracyPct)}%</div>
          <div className="profile-muted">
            Runs: {data.overall.total_runs} · Attempts: {data.overall.total_attempts} · Decisions: {data.overall.decision_events}
          </div>
        </div>

        <div className="profile-card">
          <div className="profile-card-title">Risk actions before decision</div>
          <div className="profile-muted">
            Link clicks before deciding: <strong>{Math.round(linkBeforePct)}%</strong>
            <br />
            Attachment opens before deciding: <strong>{Math.round(attachBeforePct)}%</strong>
          </div>
        </div>
      </div>

      <div className="profile-card" style={{ marginTop: 14 }}>
        <div className="profile-card-title">Per-level performance</div>

        {data.by_level.length === 0 ? (
          <div className="profile-muted">No completed levels yet.</div>
        ) : (
          <div className="profile-table-wrap">
            <table className="profile-table">
              <thead>
                <tr>
                  <th>Level</th>
                  <th>Scenario</th>
                  <th>Runs</th>
                  <th>Correct</th>
                  <th>Incorrect</th>
                  <th>Accuracy</th>
                  <th>Last played</th>
                </tr>
              </thead>
              <tbody>
                {data.by_level.map((r) => (
                  <tr key={`${r.level_number}-${r.scenario_id ?? 'na'}`}>
                    <td>{r.level_number}</td>
                    <td>{r.scenario_id ?? '-'}</td>
                    <td>{r.runs}</td>
                    <td>{r.correct}</td>
                    <td>{r.incorrect}</td>
                    <td>{Math.round(asPercent(r.accuracy))}%</td>
                    <td>{r.last_played_at ? new Date(r.last_played_at).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="profile-card" style={{ marginTop: 14 }}>
        <div className="profile-card-title">Recent runs</div>

        {data.recent_runs.length === 0 ? (
          <div className="profile-muted">No runs yet.</div>
        ) : (
          <div className="profile-table-wrap">
            <table className="profile-table">
              <thead>
                <tr>
                  <th>Mode</th>
                  <th>Scenario</th>
                  <th>Level</th>
                  <th>Emails</th>
                  <th>Correct</th>
                  <th>Incorrect</th>
                  <th>Completed</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_runs.map((r, idx) => (
                  <tr key={r.id ?? idx}>
                    <td>{r.mode ?? '-'}</td>
                    <td>{r.scenario_id ?? '-'}</td>
                    <td>{r.level_number ?? '-'}</td>
                    <td>{r.emails_total ?? '-'}</td>
                    <td>{r.correct ?? '-'}</td>
                    <td>{r.incorrect ?? '-'}</td>
                    <td>{r.completed_at ? new Date(r.completed_at).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {data.trends?.accuracy?.length > 0 && (
        <div className="profile-card" style={{ marginTop: 14 }}>
          <div className="profile-card-title">Improvement over time</div>
          <ul className="profile-trend">
            {data.trends.accuracy.map((t) => (
              <li key={t.date}>
                <strong>{t.date}</strong>: accuracy {Math.round(asPercent(t.accuracy))}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ProfileView;
