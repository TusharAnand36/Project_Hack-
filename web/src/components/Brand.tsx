export function CompassMark({ className = "" }: { className?: string }) {
  return (
    <svg className={className} width="36" height="36" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <circle cx="20" cy="20" r="17" stroke="currentColor" strokeWidth="1.5" />
      <path d="m26.5 12-3.8 11-9.2 5 3.8-11 9.2-5Z" fill="currentColor" />
      <path d="M20 0v6m0 28v6M0 20h6m28 0h6" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="20" cy="20" r="2" fill="var(--brand-paper, white)" />
    </svg>
  );
}
