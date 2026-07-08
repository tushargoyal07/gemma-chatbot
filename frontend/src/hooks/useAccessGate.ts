import { useCallback, useState } from 'react'

import { getAccessCode } from '../api/authHeaders'

export type AccessGateState = 'required' | 'granted'

export function useAccessGate() {
  const [state, setState] = useState<AccessGateState>(() =>
    getAccessCode() ? 'granted' : 'required',
  )

  const grantAccess = useCallback(() => {
    setState('granted')
  }, [])

  return { state, grantAccess }
}
