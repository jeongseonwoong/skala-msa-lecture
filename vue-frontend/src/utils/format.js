export function formatWon(value) {
  const n = Number(value ?? 0)
  if (Number.isNaN(n)) return '-'
  return `${n.toLocaleString()}원`
}

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined) return '-'
  const n = Number(value)
  if (Number.isNaN(n)) return '-'
  return `${n.toFixed(digits)}%`
}

export function formatRelativeDays(days) {
  if (days === null || days === undefined) return '-'
  if (days === 0) return '오늘'
  return `${days}일 전`
}
