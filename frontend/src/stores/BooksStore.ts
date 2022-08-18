import { writable, Writable } from 'svelte/store'

export const otBookStore: Writable<Array<[string, string]>> = writable<
  Array<[string, string]>
>([])
export const ntBookStore: Writable<Array<[string, string]>> = writable<
  Array<[string, string]>
>([])
