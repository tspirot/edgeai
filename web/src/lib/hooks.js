import { useEffect, useState } from 'react'

export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() =>
    typeof window !== 'undefined' && window.matchMedia
      ? window.matchMedia(query).matches
      : false,
  )
  useEffect(() => {
    if (!window.matchMedia) return
    const mq = window.matchMedia(query)
    const on = () => setMatches(mq.matches)
    on()
    mq.addEventListener('change', on)
    return () => mq.removeEventListener('change', on)
  }, [query])
  return matches
}

export const useReducedMotion = () =>
  useMediaQuery('(prefers-reduced-motion: reduce)')

export const useIsMobile = () => useMediaQuery('(max-width: 820px)')

// Схеме прелазе са водоравног на усправан распоред пре мобилног прелома.
export const useIsNarrow = () => useMediaQuery('(max-width: 700px)')
