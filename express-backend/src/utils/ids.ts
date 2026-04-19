export function createReference(prefix: string): string {
  const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 12)
  const random = Math.random().toString(36).slice(2, 8).toUpperCase()
  return `${prefix}${timestamp}${random}`
}
