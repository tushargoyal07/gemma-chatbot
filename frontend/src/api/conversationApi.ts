import axios from 'axios'

import { apiHeaders } from './authHeaders'
import type {
  ConversationDetail,
  ConversationSummary,
  CreateConversationResponse,
} from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

apiClient.interceptors.request.use((config) => {
  const key = apiHeaders()['X-API-Key']
  if (key) {
    config.headers.set('X-API-Key', key)
  }
  return config
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
