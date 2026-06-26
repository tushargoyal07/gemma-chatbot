import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [input, setInput] = useState('')

  const submit = () => {
    const trimmed = input.trim()
    if (!trimmed || disabled) {
      return
    }

    onSend(trimmed)
    setInput('')
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    submit()
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="chat-input-wrapper">
        <textarea
          className="chat-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          rows={1}
          disabled={disabled}
          aria-label="Message input"
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !input.trim()}
          aria-label="Send message"
        >
          <Send size={18} aria-hidden="true" />
        </button>
      </div>
      <p className="input-hint">Press Enter to send, Shift+Enter for a new line</p>
    </form>
  )
}
