import { useCallback, useEffect, useState } from 'react'

import {
  createConversation,
  deleteConversation,
  listConversations,
} from '../api/conversationApi'
import { getErrorMessage } from '../api/chatApi'
import type { ConversationSummary } from '../types/chat'

export function useConversations() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const items = await listConversations()
      setConversations(items)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const startConversation = useCallback(async () => {
    const created = await createConversation()
    setConversations((current) => [
      { id: created.id, title: created.title, updated_at: created.created_at },
      ...current,
    ])
    return created.id
  }, [])

  const removeConversation = useCallback(
    async (id: string) => {
      await deleteConversation(id)
      setConversations((current) => current.filter((item) => item.id !== id))
    },
    [],
  )

  const bumpConversation = useCallback((id: string, title?: string) => {
    setConversations((current) => {
      const index = current.findIndex((item) => item.id === id)
      if (index === -1) {
        return current
      }
      const updated = { ...current[index], updated_at: new Date().toISOString() }
      if (title) {
        updated.title = title
      }
      const next = [...current]
      next.splice(index, 1)
      return [updated, ...next]
    })
  }, [])

  return {
    conversations,
    isLoading,
    error,
    refresh,
    startConversation,
    removeConversation,
    bumpConversation,
  }
}
