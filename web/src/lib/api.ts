// Typed fetch helpers. Every API response is { snapshot, data, ...extra }.
export type Snapshot = { id: string; built_at: string; schema_version: string; anonymized: boolean };
export type ApiResponse<T> = { snapshot: Snapshot; data: T; [k: string]: unknown };

export class ApiError extends Error {
  constructor(public status: number, public detail: unknown) {
    super(typeof detail === 'string' ? detail : `API error ${status}`);
  }
}

export async function api<T = any>(path: string, params: Record<string, string | number | undefined | null> = {}): Promise<ApiResponse<T>> {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== null && v !== '') q.set(k, String(v));
  const r = await fetch(`/api/v1${path}${q.size ? `?${q}` : ''}`);
  if (!r.ok) {
    let detail: unknown = r.statusText;
    try { detail = (await r.json()).detail; } catch { /* not json */ }
    throw new ApiError(r.status, detail);
  }
  return r.json();
}
