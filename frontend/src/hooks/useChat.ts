import { useCallback, useState } from 'react'

import { getConversation } from '../api/conversationApi'
import { getErrorMessage, streamChatMessage } from '../api/chatApi'
import type { ChatMessage } from '../types/chat'

interface UseChatOptions {
  conversationId: string | null
  onConversationActivity?: (id: string, title?: string) => void
  onEnsureConversation?: () => Promise<string>
}

export function useChat({
  conversationId,
  onConversationActivity,
  onEnsureConversation,
}: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    conversationId,
  )

  const resetMessages = useCallback(() => {
    setMessages([])
    setError(null)
    setIsLoading(false)
  }, [])

  const loadConversation = useCallback(async (id: string) => {
    setError(null)
    setIsLoading(true)
    try {
      const detail = await getConversation(id)
      setMessages(detail.messages)
      setActiveConversationId(id)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearChat = useCallback(() => {
    resetMessages()
    setActiveConversationId(null)
  }, [resetMessages])

  const sendMessage = useCallback(
    async (content: string) => {
      const trimmed = content.trim()
      if (!trimmed) {
        return
      }

      let nextMessages: ChatMessage[] = []
      let currentConversationId = activeConversationId

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

      const isFirstMessage = nextMessages.length === 1

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: '',
          isStreaming: true,
          isModelLoading: isFirstMessage,
        },
      ])

      try {
        if (!currentConversationId && onEnsureConversation) {
          currentConversationId = await onEnsureConversation()
          setActiveConversationId(currentConversationId)
        }

        await streamChatMessage({
          request: {
            messages: nextMessages,
            conversation_id: currentConversationId ?? undefined,
          },
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
                isModelLoading: false,
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

        if (currentConversationId && onConversationActivity) {
          const title =
            nextMessages.length === 1
              ? trimmed.length > 60
                ? `${trimmed.slice(0, 59)}…`
                : trimmed
              : undefined
          onConversationActivity(currentConversationId, title)
        }
      } catch (err) {
        const errorMessage = getErrorMessage(err)
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
            isModelLoading: false,
            error: errorMessage,
          }
          return updated
        })
      } finally {
        setIsLoading(false)
      }
    },
    [activeConversationId, isLoading, onConversationActivity, onEnsureConversation],
  )

  const dismissError = useCallback(() => {
    setError(null)
  }, [])

  const beginNewConversation = useCallback((id: string) => {
    resetMessages()
    setActiveConversationId(id)
  }, [resetMessages])

  return {
    messages,
    isLoading,
    error,
    activeConversationId,
    sendMessage,
    clearChat,
    loadConversation,
    resetMessages,
    beginNewConversation,
    dismissError,
  }
}
