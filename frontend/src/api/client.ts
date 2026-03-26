function apiBase(): string {
  const raw = import.meta.env.VITE_API_BASE ?? "/api";
  return raw.replace(/\/$/, "");
}

export async function apiGet<T>(path: string): Promise<T> {
  const p = path.startsWith("/") ? path.slice(1) : path;
  const url = `${apiBase()}/${p}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
