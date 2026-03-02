export function clamp01(x: number) {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

export function asPct01(v: number) {
  // supports either 0..1 or 0..100
  if (!Number.isFinite(v)) return 0;
  return v <= 1 ? v : v / 100;
}

export function mean(xs: number[]) {
  const clean = xs.filter((n) => Number.isFinite(n));
  if (clean.length === 0) return 0;
  return clean.reduce((a, b) => a + b, 0) / clean.length;
}

/**
 * Linear regression slope over equally spaced x = 0..n-1.
 * Returns slope in "units per run" (here: pct points per run if input is 0..1 accuracy).
 */
export function slopePerRun(values: number[]) {
  const ys = values.map(asPct01);
  const n = ys.length;
  if (n < 2) return 0;

  // x = 0..n-1
  const xMean = (n - 1) / 2;
  const yMean = mean(ys);

  let num = 0;
  let den = 0;
  for (let i = 0; i < n; i++) {
    const dx = i - xMean;
    const dy = ys[i] - yMean;
    num += dx * dy;
    den += dx * dx;
  }
  if (den === 0) return 0;

  return num / den; // accuracy-per-run (0..1 per run)
}

export function formatPp(v01: number) {
  // v01 is in 0..1 space; format as percentage points
  const pp = v01 * 100;
  const sign = pp > 0 ? '+' : '';
  return `${sign}${pp.toFixed(1)}pp`;
}

export function rollingTrend(values: number[], window = 5) {
  const ys = values.map(asPct01);
  const n = ys.length;
  if (n === 0) {
    return { recentAvg: 0, prevAvg: 0, delta: 0, slope: 0 };
  }

  const w = Math.max(2, Math.min(window, Math.floor(n / 2) || window));
  const recent = ys.slice(-w);
  const prev = ys.slice(-2 * w, -w);

  const recentAvg = mean(recent);
  const prevAvg = prev.length ? mean(prev) : mean(ys.slice(0, Math.max(1, n - w)));
  const delta = recentAvg - prevAvg;
  const slope = slopePerRun(ys.slice(-Math.max(w, 6))); // slightly longer for stability

  return { recentAvg, prevAvg, delta, slope };
}
