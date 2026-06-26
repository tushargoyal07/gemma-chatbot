export function LoadingIndicator() {
  return (
    <div className="message-row message-row--assistant">
      <div className="message-bubble message-bubble--assistant message-bubble--loading">
        <span className="message-role">Gemma</span>
        <div className="typing-indicator" aria-label="Assistant is typing">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  )
}
