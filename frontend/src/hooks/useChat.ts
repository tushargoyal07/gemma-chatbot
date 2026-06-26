import { useCallback, useState } from 'react'

import { getErrorMessage, streamChatMessage } from '../api/chatApi'
import type { ChatMessage } from '../types/chat'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
    setIsLoading(false)
  }, [])

  const sendMessage = useCallback(async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed) {
      return
    }

    let nextMessages: ChatMessage[] = []

    setMessages((current) => {
      if (isLoading) {
        return current
      }

      const userMessage: ChatMessage = { role: 'user', content: trimmed }
      nextMessages = [...current, userMessage]
      return nextMessages
    })

    if (nextMessages.length === 0) {
      return
    }

    setIsLoading(true)
    setError(null)

    setMessages((current) => [
      ...current,
      { role: 'assistant', content: '', isStreaming: true },
    ])

    try {
      await streamChatMessage({
        request: { messages: nextMessages },
        onToken: (token) => {
          setMessages((current) => {
            const updated = [...current]
            const lastIndex = updated.length - 1
            const last = updated[lastIndex]

            if (!last || last.role !== 'assistant') {
              return current
            }

            updated[lastIndex] = {
              ...last,
              content: last.content + token,
            }
            return updated
          })
        },
        onDone: (usage) => {
          setMessages((current) => {
            const updated = [...current]
            const lastIndex = updated.length - 1
            const last = updated[lastIndex]

            if (!last || last.role !== 'assistant') {
              return current
            }

            updated[lastIndex] = {
              ...last,
              isStreaming: false,
              usage,
            }
            return updated
          })
        },
      })
    } catch (err) {
      setError(getErrorMessage(err))
      setMessages((current) => (current.length >= 2 ? current.slice(0, -2) : current.slice(0, -1)))
    } finally {
      setIsLoading(false)
    }
  }, [isLoading])

  const dismissError = useCallback(() => {
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    dismissError,
  }
}
