export default function BrandMark({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <rect x="4" y="4" width="56" height="56" rx="14" fill="none" stroke="currentColor" strokeWidth="3" opacity="0.35" />
      <g stroke="currentColor" strokeWidth="3" strokeLinecap="round">
        <path d="M20 32h9M35 32h9M32 20v9M32 35v9" />
      </g>
      <circle cx="32" cy="32" r="5" fill="var(--brass)" />
      <g fill="currentColor">
        <circle cx="18" cy="32" r="3" /><circle cx="46" cy="32" r="3" />
        <circle cx="32" cy="18" r="3" /><circle cx="32" cy="46" r="3" />
      </g>
    </svg>
  )
}
