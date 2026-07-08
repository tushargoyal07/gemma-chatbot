import axios from 'axios'

import { apiHeaders } from './authHeaders'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface AuthStatus {
  access_code_required: boolean
}

export async function fetchAuthStatus(): Promise<AuthStatus> {
  const response = await axios.get<AuthStatus>(`${API_BASE_URL}/auth/status`, {
    timeout: 10000,
  })
  return response.data
}

export async function verifyAccessCode(code: string): Promise<void> {
  await axios.post(
    `${API_BASE_URL}/auth/verify`,
    { code },
    {
      headers: apiHeaders(true),
      timeout: 10000,
    },
  )
}

export function getAuthErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (!error.response) {
      return 'Unable to reach the server. Make sure the backend is running.'
    }
    if (error.response.status === 401) {
      return 'Invalid access code. Try again.'
    }
  }
  return 'Something went wrong. Please try again.'
}
