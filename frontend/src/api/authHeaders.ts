const ACCESS_CODE_STORAGE_KEY = 'gemma_access_code'

export function getAccessCode(): string | undefined {
  const stored = sessionStorage.getItem(ACCESS_CODE_STORAGE_KEY)
  if (stored?.trim()) {
    return stored.trim()
  }
  return undefined
}

export function setAccessCode(code: string): void {
  sessionStorage.setItem(ACCESS_CODE_STORAGE_KEY, code.trim())
}

export function clearAccessCode(): void {
  sessionStorage.removeItem(ACCESS_CODE_STORAGE_KEY)
}

export function apiHeaders(includeJson = false): Record<string, string> {
  const headers: Record<string, string> = {}
  if (includeJson) {
    headers['Content-Type'] = 'application/json'
  }
  const key = getAccessCode()
  if (key) {
    headers['X-API-Key'] = key
  }
  return headers
}
