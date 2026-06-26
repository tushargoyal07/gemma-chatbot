import { ChatWindow } from './components/ChatWindow'
import { Sidebar } from './components/Sidebar'
import { useChat } from './hooks/useChat'
import './App.css'

function App() {
  const { messages, isLoading, error, sendMessage, clearChat, dismissError } = useChat()

  return (
    <div className="app-layout">
      <Sidebar onNewChat={clearChat} disabled={isLoading} />
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
