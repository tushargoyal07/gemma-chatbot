import ReactMarkdown from 'react-markdown'

import type { ChatMessage } from '../types/chat'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isStreaming = message.isStreaming === true

  return (
    <div className={`message-row ${isUser ? 'message-row--user' : 'message-row--assistant'}`}>
      <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--assistant'}`}>
        <span className="message-role">{isUser ? 'You' : 'Gemma'}</span>
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : isStreaming && !message.content ? (
          <div className="typing-indicator" aria-label="Assistant is typing">
            <span />
            <span />
            <span />
          </div>
        ) : isStreaming ? (
          <p className="message-text message-text--streaming">
            {message.content}
            <span className="stream-cursor" aria-hidden="true" />
          </p>
        ) : message.content ? (
          <>
            <div className="message-markdown">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
            {message.usage && (
              <p className="message-usage">
                {message.usage.prompt_tokens} in · {message.usage.completion_tokens} out ·{' '}
                {message.usage.total_tokens} total
              </p>
            )}
          </>
        ) : (
          <p className="message-text message-text--empty">No response text was returned.</p>
        )}
      </div>
    </div>
  )
}
