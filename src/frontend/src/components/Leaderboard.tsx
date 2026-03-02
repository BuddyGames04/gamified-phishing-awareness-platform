import React, { useEffect, useMemo, useState } from 'react';
import '../styles/MenuScreens.css';
import {
  fetchLeaderboard,
  LeaderboardMode,
  LeaderboardRow,
  LeaderboardSort,
} from '../api';

type Props = {
  onBack?: () => void;
};

// -----------------------------
// Algorithms showcase
// -----------------------------

// 0) Simple "string slicing" helper for display + for optional prefix filter
function slicePreview(s: string, max = 18): string {
  const t = String(s ?? '');
  if (t.length <= max) return t;
  return `${t.slice(0, max)}…`; // string slicing
}

// 1) String match (simple)
function containsQuerySimple(haystack: string, needle: string): boolean {
  return haystack.toLowerCase().includes(needle.toLowerCase());
}

// 1b) KMP (Knuth Morris Pratt flex)
function buildKmpTable(pattern: string): number[] {
  const p = pattern.toLowerCase();
  const table = new Array(p.length).fill(0);
  let j = 0;

  for (let i = 1; i < p.length; i++) {
    while (j > 0 && p[i] !== p[j]) j = table[j - 1];
    if (p[i] === p[j]) j++;
    table[i] = j;
  }
  return table;
}

function containsQueryKmp(haystack: string, needle: string): boolean {
  const h = haystack.toLowerCase();
  const n = needle.toLowerCase();
  if (!n) return true;
  if (n.length > h.length) return false;

  const table = buildKmpTable(n);
  let j = 0;

  for (let i = 0; i < h.length; i++) {
    while (j > 0 && h[i] !== n[j]) j = table[j - 1];
    if (h[i] === n[j]) j++;
    if (j === n.length) return true;
  }
  return false;
}

// 2) Merge sort 
function mergeSort<T>(arr: T[], cmp: (a: T, b: T) => number): T[] {
  if (arr.length <= 1) return arr.slice();

  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid), cmp);
  const right = mergeSort(arr.slice(mid), cmp);

  const out: T[] = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    // stable: <= takes from left first on ties
    if (cmp(left[i], right[j]) <= 0) out.push(left[i++]);
    else out.push(right[j++]);
  }

  while (i < left.length) out.push(left[i++]);
  while (j < right.length) out.push(right[j++]);

  return out;
}

// 2b) Bubble sort (educational - slow on purpose)
function bubbleSort<T>(arr: T[], cmp: (a: T, b: T) => number): T[] {
  const out = arr.slice();
  const n = out.length;
  let swapped = true;

  for (let pass = 0; pass < n - 1 && swapped; pass++) {
    swapped = false;
    for (let i = 0; i < n - 1 - pass; i++) {
      if (cmp(out[i], out[i + 1]) > 0) {
        const tmp = out[i];
        out[i] = out[i + 1];
        out[i + 1] = tmp;
        swapped = true;
      }
    }
  }
  return out;
}

// inear search to find a specific user id
function linearSearchUserIndex(rows: LeaderboardRow[], userId: string): number {
  const target = (userId ?? '').trim().toLowerCase();
  if (!target) return -1;
  for (let i = 0; i < rows.length; i++) {
    if (String(rows[i].user_id ?? '').toLowerCase() === target) return i;
  }
  return -1;
}

// -----------------------------
// Helpers
// -----------------------------

function fmtMs(ms: number | null): string {
  if (ms == null) return '—';
  const s = Math.round(ms / 1000);
  const mm = Math.floor(s / 60);
  const ss = s % 60;
  return `${mm}:${String(ss).padStart(2, '0')}`;
}

function clampInt(n: number, lo: number, hi: number): number {
  if (Number.isNaN(n)) return lo;
  return Math.max(lo, Math.min(hi, n));
}

function safeNum(x: any, fallback = 0): number {
  const n = Number(x);
  return Number.isFinite(n) ? n : fallback;
}

const Leaderboard: React.FC<Props> = ({ onBack }) => {
  const [mode, setMode] = useState<LeaderboardMode>('overall');
  const [sortDir, setSortDir] = useState<LeaderboardSort>('desc');
  const [limit, setLimit] = useState<number>(50);

  const [q, setQ] = useState('');
  const [useKmp, setUseKmp] = useState(false);

  // sorting algorithm toggles
  const [sortAlgo, setSortAlgo] = useState<'merge' | 'bubble' | 'native'>('merge');

  // extra “string slicing” / prefix filter toggle
  const [prefixOnly, setPrefixOnly] = useState(false);

  // simple search demo: find exact username & highlight
  const [findUser, setFindUser] = useState('');
  const [foundIndex, setFoundIndex] = useState<number>(-1);

  const [rows, setRows] = useState<LeaderboardRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // Server fetch: aggregated per mode
  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setErr(null);
      try {
        const res = await fetchLeaderboard({
          mode,
          sort: sortDir, // server may sort too; we still sort client-side for the showcase
          limit: clampInt(limit, 5, 500),
        });

        if (!cancelled) {
          const next = Array.isArray(res?.rows) ? res.rows : [];
          setRows(next);
          // reset “found” when dataset changes
          setFoundIndex(-1);
        }
      } catch (e: any) {
        if (!cancelled) setErr(String(e?.message ?? e ?? 'Failed to load leaderboard'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [mode, sortDir, limit]);

  const filteredAndSorted = useMemo(() => {
    const query = q.trim();

    // Filter: query match on user_id
    const matcher = useKmp ? containsQueryKmp : containsQuerySimple;

    const filtered = !query
      ? rows.slice()
      : rows.filter((r) => {
          const id = String(r.user_id ?? '');
          if (prefixOnly) {
            // string slicing: compare start segment only (prefix match)
            const n = query.length;
            return id.slice(0, n).toLowerCase() === query.toLowerCase();
          }
          return matcher(id, query);
        });

    // Sort comparator (primary score, secondary user_id)
    const dir = sortDir === 'asc' ? 1 : -1;

    const cmp = (a: LeaderboardRow, b: LeaderboardRow) => {
      const sa = safeNum(a.score, 0);
      const sb = safeNum(b.score, 0);
      if (sa !== sb) return (sa - sb) * dir;

      // tie-breaker for determinism
      const ua = String(a.user_id ?? '').toLowerCase();
      const ub = String(b.user_id ?? '').toLowerCase();
      if (ua < ub) return -1;
      if (ua > ub) return 1;
      return 0;
    };

    if (sortAlgo === 'native') return filtered.slice().sort(cmp);
    if (sortAlgo === 'bubble') return bubbleSort(filtered, cmp);
    return mergeSort(filtered, cmp);
  }, [rows, q, sortDir, useKmp, sortAlgo, prefixOnly]);

  // update “found index” when user searches exact username OR list changes
  useEffect(() => {
    const idx = linearSearchUserIndex(filteredAndSorted, findUser);
    setFoundIndex(idx);
  }, [findUser, filteredAndSorted]);

  const displayRows = filteredAndSorted;

  return (
    <div className="screen-shell">
      <div className="screen-card">
        <div className="screen-header">
          <div className="brand">
            <div className="brand-badge">PA</div>
            <div>
              <h1 className="screen-title">Leaderboard</h1>
              <p className="screen-subtitle">
                Server aggregates. Client demonstrates filter/search + merge sort / bubble sort.
              </p>
            </div>
          </div>

          {onBack && (
            <button className="ms-btn ms-btn-ghost" onClick={onBack}>
              ← Back
            </button>
          )}
        </div>

        <div className="screen-body">
          {/* Controls */}
          <div
            style={{
              display: 'flex',
              gap: 12,
              flexWrap: 'wrap',
              alignItems: 'center',
              marginBottom: 12,
            }}
          >
            {/* Mode */}
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Mode</span>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as LeaderboardMode)}
              >
                <option value="overall">Overall</option>
                <option value="arcade">Arcade</option>
                <option value="simulation">Simulation</option>
                <option value="pvp">PVP</option>
              </select>
            </label>

            {/* Sort */}
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Sort</span>
              <select
                value={sortDir}
                onChange={(e) => setSortDir(e.target.value as LeaderboardSort)}
              >
                <option value="desc">Score ↓</option>
                <option value="asc">Score ↑</option>
              </select>
            </label>

            {/* Sorting algorithm */}
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Algorithm</span>
              <select
                value={sortAlgo}
                onChange={(e) => setSortAlgo(e.target.value as any)}
                title="Sort algorithm used on the client"
              >
                <option value="merge">Merge sort (stable)</option>
                <option value="bubble">Bubble sort (slow)</option>
                <option value="native">Native sort()</option>
              </select>
            </label>

            {/* Limit */}
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Limit</span>
              <input
                type="number"
                value={limit}
                min={5}
                max={500}
                onChange={(e) => setLimit(clampInt(parseInt(e.target.value || '50', 10), 5, 500))}
                style={{ width: 90 }}
              />
            </label>

            {/* Query */}
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Filter</span>
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="username contains…"
                style={{ width: 220 }}
              />
            </label>

            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={useKmp}
                onChange={(e) => setUseKmp(e.target.checked)}
              />
              <span style={{ fontSize: 12, opacity: 0.9 }}>Use KMP match</span>
            </label>

            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={prefixOnly}
                onChange={(e) => setPrefixOnly(e.target.checked)}
              />
              <span style={{ fontSize: 12, opacity: 0.9 }}>Prefix only (slice)</span>
            </label>
          </div>

          {/* Simple search demo */}
          <div
            style={{
              display: 'flex',
              gap: 10,
              flexWrap: 'wrap',
              alignItems: 'center',
              marginBottom: 12,
              opacity: 0.95,
            }}
          >
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, opacity: 0.85 }}>Find exact user</span>
              <input
                value={findUser}
                onChange={(e) => setFindUser(e.target.value)}
                placeholder="e.g. Luke"
                style={{ width: 220 }}
              />
            </label>
            <div style={{ fontSize: 12, opacity: 0.85 }}>
              {findUser.trim()
                ? foundIndex >= 0
                  ? `Found at position #${foundIndex + 1} (linear search)`
                  : 'Not found (linear search)'
                : 'Type a username to run linear search'}
            </div>
          </div>

          {/* Status */}
          {err && (
            <div style={{ marginBottom: 10, color: '#ffb4b4', fontSize: 13 }}>
              {err}
            </div>
          )}
          {loading && (
            <div style={{ marginBottom: 10, opacity: 0.85, fontSize: 13 }}>
              Loading…
            </div>
          )}

          {/* Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', opacity: 0.9 }}>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    #
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Username
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Score
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Runs
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Correct
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Incorrect
                  </th>
                  <th style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                    Avg time
                  </th>
                </tr>
              </thead>

              <tbody>
                {displayRows.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ padding: 12, opacity: 0.85 }}>
                      {loading ? 'Loading…' : 'No results.'}
                    </td>
                  </tr>
                ) : (
                  displayRows.map((r, idx) => {
                    const isFound = foundIndex === idx && findUser.trim().length > 0;

                    return (
                      <tr
                        key={`${r.user_id}-${idx}`}
                        style={{
                          background: isFound
                            ? 'rgba(255, 215, 0, 0.14)'
                            : idx % 2 === 0
                              ? 'transparent'
                              : 'rgba(255,255,255,0.03)',
                        }}
                        title={isFound ? 'Matched by linear search' : undefined}
                      >
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          {idx + 1}
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          <span title={String(r.user_id ?? '')}>{slicePreview(String(r.user_id ?? ''), 24)}</span>
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          <strong>{safeNum(r.score, 0)}</strong>
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          {safeNum(r.runs, 0)}
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          {safeNum(r.correct, 0)}
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          {safeNum(r.incorrect, 0)}
                        </td>
                        <td style={{ padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          {fmtMs(r.avg_duration_ms ?? null)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Tiny footer note */}
          <div style={{ marginTop: 10, fontSize: 12, opacity: 0.75 }}>
            Client-side demo: filter uses {useKmp ? 'KMP' : 'includes'}; prefix mode uses{' '}
            <code>slice()</code>; sorting uses{' '}
            {sortAlgo === 'merge' ? 'merge sort' : sortAlgo === 'bubble' ? 'bubble sort' : 'native sort'}; “Find exact user”
            uses linear search.
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;