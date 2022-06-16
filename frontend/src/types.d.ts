export type AssemblyStrategy = {
  id: string
  label: string
}

// NOTE the following is for the next version of the frontend, including now
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

export type JsonString = { [key: string]: string }
export type JsonBool = { [key: string]: boolean }
