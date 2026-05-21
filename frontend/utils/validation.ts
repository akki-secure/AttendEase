export const ASCII_ONLY = /^[\x20-\x7E]+$/

export function extractApiError(err: unknown, fallback: string): string {
  const e = err as { data?: { detail?: string } }
  return e?.data?.detail ?? fallback
}
