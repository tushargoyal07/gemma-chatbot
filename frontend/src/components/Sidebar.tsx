import { MessageSquarePlus, Trash2 } from 'lucide-react'

import type { ConversationSummary } from '../types/chat'

interface SidebarProps {
  conversations: ConversationSummary[]
  activeConversationId: string | null
  isLoadingConversations?: boolean
  onNewChat: () => void
  onSelectConversation: (id: string) => void
  onDeleteConversation?: (id: string) => void
  disabled?: boolean
}

function formatRelativeTime(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export function Sidebar({
  conversations,
  activeConversationId,
  isLoadingConversations = false,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  disabled = false,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Gemma Chat</h1>
        <p className="sidebar-subtitle">AI assistant</p>
      </div>

      <button
        type="button"
        className="new-chat-button"
        onClick={onNewChat}
        disabled={disabled}
      >
        <MessageSquarePlus size={18} aria-hidden="true" />
        New Chat
      </button>

      <div className="conversation-list" role="list">
        {isLoadingConversations && conversations.length === 0 && (
          <p className="conversation-list-empty">Loading chats…</p>
        )}
        {!isLoadingConversations && conversations.length === 0 && (
          <p className="conversation-list-empty">No saved chats yet</p>
        )}
        {conversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId
          return (
            <div
              key={conversation.id}
              className={`conversation-item${isActive ? ' conversation-item--active' : ''}`}
              role="listitem"
            >
              <button
                type="button"
                className="conversation-button"
                onClick={() => onSelectConversation(conversation.id)}
                disabled={disabled}
              >
                <span className="conversation-title">{conversation.title}</span>
                <span className="conversation-time">
                  {formatRelativeTime(conversation.updated_at)}
                </span>
              </button>
              {onDeleteConversation && (
                <button
                  type="button"
                  className="conversation-delete"
                  onClick={() => onDeleteConversation(conversation.id)}
                  disabled={disabled}
                  aria-label={`Delete ${conversation.title}`}
                >
                  <Trash2 size={14} aria-hidden="true" />
                </button>
              )}
            </div>
          )
        })}
      </div>

      <div className="sidebar-footer">
        <span className="model-badge">llama-3.1-8b</span>
        <span className="sidebar-note">Chats saved to server</span>
      </div>
    </aside>
  )
}
