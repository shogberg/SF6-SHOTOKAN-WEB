export const pct = (v: number | null | undefined) => (v == null ? '—' : `${v}%`);
export const num = (v: number | null | undefined, d = 1) => (v == null ? '—' : Number(v).toFixed(d).replace(/\.0+$/, ''));

// Rank shown per the review rules: Master with MR -> "1704 MR"; below Master -> league name only; else "MR unknown".
export function rank(mr?: number | null, league?: string | null) {
  if (mr) return `${mr} MR`;
  if (league) return league.split(' ')[0];
  return 'MR unknown';
}

export const contextLabel: Record<string, string> = { ranked: 'Ranked', casual: 'Casual', local: 'Local', tournament: 'Tournament', unknown: '—' };

export function parseJSON<T>(v: unknown, fallback: T): T {
  if (v == null) return fallback;
  if (typeof v !== 'string') return v as T;
  try { return JSON.parse(v) as T; } catch { return fallback; }
}
