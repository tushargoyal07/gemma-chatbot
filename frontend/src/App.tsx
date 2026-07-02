import { useCallback } from 'react'

import { ChatWindow } from './components/ChatWindow'
import { Sidebar } from './components/Sidebar'
import { useChat } from './hooks/useChat'
import { useConversations } from './hooks/useConversations'
import './App.css'

function App() {
  const {
    conversations,
    isLoading: isLoadingConversations,
    startConversation,
    removeConversation,
    bumpConversation,
  } = useConversations()

  const ensureConversation = useCallback(async () => {
    return startConversation()
  }, [startConversation])

  const {
    messages,
    isLoading,
    error,
    activeConversationId,
    sendMessage,
    loadConversation,
    clearChat,
    beginNewConversation,
    dismissError,
  } = useChat({
    conversationId: null,
    onEnsureConversation: ensureConversation,
    onConversationActivity: bumpConversation,
  })

  const handleNewChat = useCallback(async () => {
    const id = await startConversation()
    beginNewConversation(id)
  }, [beginNewConversation, startConversation])

  const handleSelectConversation = useCallback(
    async (id: string) => {
      if (id === activeConversationId) {
        return
      }
      await loadConversation(id)
    },
    [activeConversationId, loadConversation],
  )

  const handleDeleteConversation = useCallback(
    async (id: string) => {
      await removeConversation(id)
      if (id === activeConversationId) {
        clearChat()
      }
    },
    [activeConversationId, clearChat, removeConversation],
  )

  return (
    <div className="app-layout">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        isLoadingConversations={isLoadingConversations}
        onNewChat={() => void handleNewChat()}
        onSelectConversation={(id) => void handleSelectConversation(id)}
        onDeleteConversation={(id) => void handleDeleteConversation(id)}
        disabled={isLoading}
      />
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        error={error}
        onSend={sendMessage}
        onDismissError={dismissError}
      />
    </div>
  )
}

export default App
