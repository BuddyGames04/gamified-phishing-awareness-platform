import React, { useEffect, useState } from 'react';
import { fetchProfileMetrics, ProfileMetrics } from '../api';
import { rollingTrend, formatPp, asPct01 } from '../utils/metricsMath';
import '../styles/ProfileView.css';

type Props = { userId: string };
type Tab = 'main' | 'arcade' | 'pvp';

function asPercent(v: number) {
  if (!Number.isFinite(v)) return 0;
  return v <= 1 ? v * 100 : v;
}

const ProfileView: React.FC<Props> = ({ userId }) => {
  const [tab, setTab] = useState<Tab>('main');

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
  const overallAllAccuracyPct = asPercent(
    (data as any).overall_all?.accuracy ?? data.overall.accuracy
  );
  const inboxAccuracyPct = asPercent(data.overall.accuracy);
  const linkBeforePct = asPercent(data.overall.pct_link_click_before_decision);
  const attachBeforePct = asPercent(data.overall.pct_attachment_open_before_decision);

  return (
    <div className="profile-shell">
      <h2 className="profile-title">Your Profile</h2>
      <div className="profile-subtitle">
        User: <strong>{data.user_id}</strong>
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
        <button className="btn" onClick={() => setTab('main')} disabled={tab === 'main'}>
          Main
        </button>
        <button className="btn" onClick={() => setTab('arcade')} disabled={tab === 'arcade'}>
          Arcade
        </button>
        <button className="btn" onClick={() => setTab('pvp')} disabled={tab === 'pvp'}>
          PVP
        </button>
      </div>

      {tab === 'main' && (
        <>
          <div className="profile-grid">
            <div className="profile-card">
              <div className="profile-card-title">Overall (all modes)</div>
              <div className="profile-big">{Math.round(overallAllAccuracyPct)}%</div>
              <div className="profile-muted">
                Attempts: {(data as any).overall_all?.total_attempts ?? data.overall.total_attempts}
                <br />
                Arcade: {(data as any).overall_all?.arcade_attempts ?? '-'} · Inbox:{' '}
                {(data as any).overall_all?.inbox_attempts ?? '-'} · PVP:{' '}
                {(data as any).overall_all?.pvp_attempts ?? '-'}
              </div>
            </div>

            <div className="profile-card">
              <div className="profile-card-title">Inbox (curated levels)</div>
              <div className="profile-big">{Math.round(inboxAccuracyPct)}%</div>
              <div className="profile-muted">
                Runs: {data.overall.total_runs} · Attempts: {data.overall.total_attempts}
              </div>
            </div>
          </div>

          <div className="profile-card">
            <div className="profile-card-title">Risk actions before decision</div>
            <div className="profile-muted">
              Link clicks before deciding: <strong>{Math.round(linkBeforePct)}%</strong>
              <br />
              Attachment opens before deciding:{' '}
              <strong>{Math.round(attachBeforePct)}%</strong>
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
                        <td>
                          {r.last_played_at
                            ? new Date(r.last_played_at).toLocaleString()
                            : '-'}
                        </td>
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
                        <td>
                          {r.completed_at ? new Date(r.completed_at).toLocaleString() : '-'}
                        </td>
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

              <div className="profile-table-wrap">
                <table className="profile-table">
                  <thead>
                    <tr>
                      <th>Completed</th>
                      <th>Accuracy</th>
                      <th>Δ vs previous</th>
                      <th>Δ vs first</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.trends.accuracy.map((row, idx) => {
                      const acc = asPercent(row.accuracy);
                      const prev =
                        idx > 0 ? asPercent(data.trends!.accuracy[idx - 1].accuracy) : null;
                      const first = asPercent(data.trends!.accuracy[0].accuracy);

                      const deltaPrev = prev == null ? null : acc - prev;
                      const deltaFirst = acc - first;

                      const fmtDelta = (d: number | null) => {
                        if (d == null) return '-';
                        const sign = d > 0 ? '+' : '';
                        return `${sign}${Math.round(d)} pp`;
                      };

                      const completedLabel = row.date ? new Date(row.date).toLocaleString() : '-';

                      return (
                        <tr key={`${row.date ?? 'date'}-${idx}`}>
                          <td>{completedLabel}</td>
                          <td>{Math.round(acc)}%</td>
                          <td>{fmtDelta(deltaPrev)}</td>
                          <td>{fmtDelta(deltaFirst)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div className="profile-muted" style={{ marginTop: 8 }}>
                Δ values are <strong>percentage points</strong> (pp), not percent.
              </div>
            </div>
          )}
        </>
      )}

      {tab === 'arcade' && (
        <div className="profile-card" style={{ marginTop: 14 }}>
          <div className="profile-card-title">Arcade metrics</div>

          {!data.arcade ? (
            <div className="profile-muted">No arcade attempts yet.</div>
          ) : (
            <>
              <div className="profile-grid" style={{ marginTop: 10 }}>
                <div className="profile-card">
                  <div className="profile-card-title">Accuracy</div>
                  <div className="profile-big">{Math.round(asPercent(data.arcade.accuracy))}%</div>
                  <div className="profile-muted">
                    Attempts: {data.arcade.total_attempts} · Correct: {data.arcade.correct} · Incorrect:{' '}
                    {data.arcade.incorrect}
                  </div>
                </div>

                <div className="profile-card">
                  <div className="profile-card-title">Streaks</div>
                  <div className="profile-muted">
                    Current streak: <strong>{data.arcade.current_streak}</strong>
                    <br />
                    Best streak: <strong>{data.arcade.best_streak}</strong>
                  </div>
                </div>

                <div className="profile-card">
                  <div className="profile-card-title">Speed</div>
                  <div className="profile-muted">
                    Avg response time:{' '}
                    <strong>
                      {data.arcade.avg_response_time_ms != null
                        ? `${Math.round(data.arcade.avg_response_time_ms)} ms`
                        : '-'}
                    </strong>
                    <br />
                    Avg difficulty faced:{' '}
                    <strong>
                      {data.arcade.avg_email_difficulty != null
                        ? data.arcade.avg_email_difficulty.toFixed(2)
                        : '-'}
                    </strong>
                    <br />
                    Target difficulty now:{' '}
                    <strong>
                      {data.arcade.target_difficulty_now != null
                        ? data.arcade.target_difficulty_now.toFixed(2)
                        : '-'}
                    </strong>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: 12 }}>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>Accuracy by difficulty</div>
                <div className="profile-table-wrap">
                  <table className="profile-table">
                    <thead>
                      <tr>
                        <th>Bucket</th>
                        <th>Attempts</th>
                        <th>Accuracy</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.arcade.accuracy_by_difficulty_bucket.map((b) => (
                        <tr key={b.bucket}>
                          <td>{b.bucket}</td>
                          <td>{b.attempts}</td>
                          <td>{Math.round(asPercent(b.accuracy))}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {tab === 'pvp' && (
        <div className="profile-card" style={{ marginTop: 14 }}>
          <div className="profile-card-title">PVP metrics</div>

          {!data.pvp ? (
            <div className="profile-muted">No PVP activity yet.</div>
          ) : (
            <>
              <div className="profile-grid" style={{ marginTop: 10 }}>
                <div className="profile-card">
                  <div className="profile-card-title">Playing other players</div>
                  <div className="profile-big">
                    {Math.round(asPercent(data.pvp.playing.accuracy))}%
                  </div>
                  <div className="profile-muted">
                    Attempts: {data.pvp.playing.total_attempts} · Correct: {data.pvp.playing.correct} ·
                    Incorrect: {data.pvp.playing.incorrect}
                  </div>
                </div>

                <div className="profile-card">
                  <div className="profile-card-title">Players on your levels</div>
                  <div className="profile-big">
                    {Math.round(asPercent(data.pvp.creator.accuracy))}%
                  </div>
                  <div className="profile-muted">
                    Levels: {data.pvp.creator.levels_total} · Posted: {data.pvp.creator.levels_posted}
                    <br />
                    Attempts: {data.pvp.creator.total_attempts} · Correct: {data.pvp.creator.correct} ·
                    Incorrect: {data.pvp.creator.incorrect}
                    <br />
                    Unique players: {data.pvp.creator.unique_players}
                  </div>
                </div>
              </div>

              <div className="profile-card" style={{ marginTop: 14 }}>
                <div className="profile-card-title">Risk actions (PVP)</div>
                <div className="profile-muted">
                  Link clicks before deciding:{' '}
                  <strong>{Math.round(asPercent(data.pvp.playing.pct_link_before))}%</strong>
                  <br />
                  Attachment opens before deciding:{' '}
                  <strong>{Math.round(asPercent(data.pvp.playing.pct_attach_before))}%</strong>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ProfileView;