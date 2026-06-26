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
  usage?: UsageStats
}

export interface ChatRequest {
  messages: ChatMessage[]
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
