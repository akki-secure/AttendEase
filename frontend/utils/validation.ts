export const ASCII_ONLY = /^[\x20-\x7E]+$/

export function extractApiError(err: unknown, fallback: string): string {
  const e = err as { data?: { detail?: unknown }; status?: number; message?: string }
  if (typeof e?.data?.detail === "string") return e.data.detail
  if (Array.isArray(e?.data?.detail)) return e.data!.detail!.map((d: { msg?: string }) => d.msg ?? "").join(", ")
  if (e?.status) return `${fallback}（HTTP ${e.status}）`
  if (e?.message) return `${fallback}（${e.message}）`
  return fallback
}
