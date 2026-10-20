const PREFIX = 'jdp-explain:'

export function storeExplainCode(code: string): string {
  const key = (typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `k${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
  ).slice(0, 12)
  try {
    sessionStorage.setItem(PREFIX + key, code)
  } catch {
    /* quota */
  }
  return key
}

export function loadExplainCode(key: string): string | null {
  if (!key) return null
  try {
    return sessionStorage.getItem(PREFIX + key)
  } catch {
    return null
  }
}
