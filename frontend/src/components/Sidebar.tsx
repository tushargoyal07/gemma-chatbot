import { MessageSquarePlus } from 'lucide-react'

interface SidebarProps {
  onNewChat: () => void
  disabled?: boolean
}

export function Sidebar({ onNewChat, disabled = false }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Gemma Chat</h1>
        <p className="sidebar-subtitle">Local AI assistant</p>
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

      <div className="sidebar-footer">
        <span className="model-badge">gemma4:e2b</span>
        <span className="sidebar-note">Runs entirely on your machine</span>
      </div>
    </aside>
  )
}
