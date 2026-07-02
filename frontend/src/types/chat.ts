export type MessageRole = 'user' | 'assistant' | 'system'

export interface UsageStats {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface ChatMessage {
  role: MessageRole
  content: string
  isStreaming?: boolean
  isModelLoading?: boolean
  error?: string
  usage?: UsageStats
}

export interface ChatRequest {
  messages: ChatMessage[]
  conversation_id?: string
}

export interface ConversationSummary {
  id: string
  title: string
  updated_at: string
}

export interface ConversationDetail {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
}

export interface CreateConversationResponse {
  id: string
  title: string
  created_at: string
}

export interface ChatResponse {
  message: ChatMessage
  usage?: UsageStats
}

export interface ApiError {
  detail: string
}

export type StreamEvent =
  | { type: 'start' }
  | { type: 'token'; content: string }
  | { type: 'done'; usage: UsageStats }
  | { type: 'error'; message: string }
