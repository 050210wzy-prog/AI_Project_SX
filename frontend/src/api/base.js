const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || ''

export const apiBaseUrl = rawBaseUrl.replace(/\/$/, '')

export function apiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${apiBaseUrl}/api${normalizedPath}`
}

export const axiosBaseUrl = apiBaseUrl ? `${apiBaseUrl}/api` : '/api'
