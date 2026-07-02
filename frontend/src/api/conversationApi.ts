import axios from 'axios'

import type {
  ConversationDetail,
  ConversationSummary,
  CreateConversationResponse,
} from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY as string | undefined

function apiHeaders(): Record<string, string> {
  const headers: Record<string, string> = {}
  if (API_KEY?.trim()) {
    headers['X-API-Key'] = API_KEY.trim()
  }
  return headers
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: apiHeaders(),
  timeout: 30000,
})

export async function listConversations(): Promise<ConversationSummary[]> {
  const response = await apiClient.get<ConversationSummary[]>('/conversations')
  return response.data
}

export async function createConversation(
  title = 'New Chat',
): Promise<CreateConversationResponse> {
  const response = await apiClient.post<CreateConversationResponse>('/conversations', {
    title,
  })
  return response.data
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  const response = await apiClient.get<ConversationDetail>(`/conversations/${id}`)
  return response.data
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/conversations/${id}`)
}
