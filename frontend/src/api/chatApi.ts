import axios, { AxiosError } from 'axios'

import type { ChatRequest, ChatResponse, StreamEvent, UsageStats } from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY as string | undefined

function apiHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (API_KEY?.trim()) {
    headers['X-API-Key'] = API_KEY.trim()
  }
  return headers
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: apiHeaders(),
  timeout: 120000,
})

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', request)
  return response.data
}

export async function streamChatMessage({
  request,
  onToken,
  onDone,
  signal,
}: {
  request: ChatRequest
  onToken: (content: string) => void
  onDone: (usage?: UsageStats) => void
  signal?: AbortSignal
}): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: apiHeaders(),
    body: JSON.stringify({
      messages: request.messages
        .filter((message) => message.content.trim().length > 0)
        .map(({ role, content }) => ({ role, content: content.trim() })),
      ...(request.conversation_id ? { conversation_id: request.conversation_id } : {}),
    }),
    signal,
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`
    try {
      const body = (await response.json()) as {
        detail?: string | { msg: string; loc?: string[] }[]
      }
      if (typeof body.detail === 'string') {
        detail = body.detail
      } else if (Array.isArray(body.detail) && body.detail.length > 0) {
        detail = body.detail.map((item) => item.msg).join(', ')
      }
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }

  if (!response.body) {
    throw new Error('Streaming is not supported by this browser.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let receivedDone = false

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const event of events) {
      const dataLine = event.split('\n').find((line) => line.startsWith('data: '))
      if (!dataLine) {
        continue
      }

      let payload: StreamEvent
      try {
        payload = JSON.parse(dataLine.slice(6)) as StreamEvent
      } catch {
        throw new Error('Received an invalid response from the server.')
      }

      if (payload.type === 'start') {
        continue
      } else if (payload.type === 'token') {
        onToken(payload.content)
      } else if (payload.type === 'done') {
        receivedDone = true
        onDone(payload.usage)
      } else if (payload.type === 'error') {
        throw new Error(payload.message)
      }
    }
  }

  if (!receivedDone) {
    throw new Error(
      'The response ended unexpectedly. The model may still be loading — try again.',
    )
  }
}

function normalizeStreamErrorMessage(message: string): string {
  const lower = message.toLowerCase()

  if (lower.includes('not loaded') || lower.includes('pull the model')) {
    return `${message} If you're using Ollama locally, pull the model and try again.`
  }

  if (
    lower.includes('connection refused') ||
    lower.includes('failed to connect') ||
    lower.includes('network')
  ) {
    return 'Unable to reach the server. Make sure the backend is running.'
  }

  return message
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error && error.name === 'AbortError') {
    return 'Request was cancelled.'
  }

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string | { msg: string }[] }>

    if (axiosError.response?.data?.detail) {
      const { detail } = axiosError.response.data
      if (typeof detail === 'string') {
        return detail
      }
      if (Array.isArray(detail) && detail.length > 0) {
        return detail.map((item) => item.msg).join(', ')
      }
    }

    if (axiosError.code === 'ECONNABORTED') {
      return 'Request timed out. The model may still be loading — try again.'
    }

    if (!axiosError.response) {
      return 'Unable to reach the server. Make sure the backend is running.'
    }

    return `Request failed with status ${axiosError.response.status}.`
  }

  if (error instanceof TypeError) {
    return 'Unable to reach the server. Make sure the backend is running.'
  }

  if (error instanceof Error) {
    return normalizeStreamErrorMessage(error.message)
  }

  return 'An unexpected error occurred.'
}
