import { useRef, useState, type ClipboardEvent, type FormEvent } from 'react'

import { getAuthErrorMessage, verifyAccessCode } from '../api/authApi'
import { setAccessCode } from '../api/authHeaders'

interface AccessGateProps {
  onSuccess: () => void
}

export function AccessGate({ onSuccess }: AccessGateProps) {
  const [digits, setDigits] = useState(['', '', '', '', '', ''])
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const inputRefs = useRef<Array<HTMLInputElement | null>>([])

  const code = digits.join('')

  const focusInput = (index: number) => {
    inputRefs.current[index]?.focus()
  }

  const handleChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, '').slice(-1)
    const next = [...digits]
    next[index] = digit
    setDigits(next)
    setError(null)

    if (digit && index < 5) {
      focusInput(index + 1)
    }
  }

  const handleKeyDown = (index: number, key: string) => {
    if (key === 'Backspace' && !digits[index] && index > 0) {
      focusInput(index - 1)
    }
  }

  const handlePaste = (event: ClipboardEvent<HTMLInputElement>) => {
    event.preventDefault()
    const pasted = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (!pasted) {
      return
    }

    const next = [...digits]
    for (let i = 0; i < 6; i += 1) {
      next[i] = pasted[i] ?? ''
    }
    setDigits(next)
    setError(null)
    focusInput(Math.min(pasted.length, 5))
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (code.length !== 6 || isSubmitting) {
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      await verifyAccessCode(code)
      setAccessCode(code)
      onSuccess()
    } catch (submitError) {
      setError(getAuthErrorMessage(submitError))
      setDigits(['', '', '', '', '', ''])
      focusInput(0)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="access-gate">
      <div className="access-gate-card">
        <h1 className="access-gate-title">Gemma Chatbot</h1>
        <p className="access-gate-subtitle">Enter the 6-digit access code to continue</p>

        <form className="access-gate-form" onSubmit={(event) => void handleSubmit(event)}>
          <div className="access-code-inputs" aria-label="6-digit access code">
            {digits.map((digit, index) => (
              <input
                key={index}
                ref={(element) => {
                  inputRefs.current[index] = element
                }}
                className="access-code-digit"
                type="text"
                inputMode="numeric"
                autoComplete={index === 0 ? 'one-time-code' : 'off'}
                maxLength={1}
                value={digit}
                disabled={isSubmitting}
                autoFocus={index === 0}
                aria-label={`Digit ${index + 1}`}
                onChange={(event) => handleChange(index, event.target.value)}
                onKeyDown={(event) => handleKeyDown(index, event.key)}
                onPaste={handlePaste}
              />
            ))}
          </div>

          {error ? <p className="access-gate-error">{error}</p> : null}

          <button
            type="submit"
            className="access-gate-submit"
            disabled={code.length !== 6 || isSubmitting}
          >
            {isSubmitting ? 'Checking…' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  )
}
