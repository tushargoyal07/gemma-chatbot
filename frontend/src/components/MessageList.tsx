import { useEffect, useRef } from 'react'

import type { ChatMessage } from '../types/chat'
import { MessageBubble } from './MessageBubble'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading: boolean
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const isStreaming = messages.some((message) => message.isStreaming)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: isStreaming ? 'auto' : 'smooth' })
  }, [messages, isLoading, isStreaming])

  return (
    <div className="message-list">
      {messages.length === 0 && !isLoading && (
        <div className="empty-state">
          <h2>How can I help you today?</h2>
          <p>Ask anything — your chats are saved on the server.</p>
        </div>
      )}

      {messages.map((message, index) => (
        <MessageBubble key={`${message.role}-${index}`} message={message} />
      ))}

      <div ref={bottomRef} />
    </div>
  )
}
