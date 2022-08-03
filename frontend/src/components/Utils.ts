export function isEmpty(value: string | null | undefined): boolean {
  return value === undefined || value === null || value.trim()?.length === 0
}
