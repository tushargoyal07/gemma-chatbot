import type { ChatMessage } from '../types/chat'
import { ChatInput } from './ChatInput'
import { ErrorBanner } from './ErrorBanner'
import { MessageList } from './MessageList'

interface ChatWindowProps {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  onSend: (message: string) => void
  onDismissError: () => void
}

export function ChatWindow({
  messages,
  isLoading,
  error,
  onSend,
  onDismissError,
}: ChatWindowProps) {
  return (
    <main className="chat-window">
      <header className="chat-header">
        <h2>Chat</h2>
      </header>

      {error && <ErrorBanner message={error} onDismiss={onDismissError} />}

      <MessageList messages={messages} isLoading={isLoading} />

      <div className="chat-input-container">
        <ChatInput onSend={onSend} disabled={isLoading} />
      </div>
    </main>
  )
}
