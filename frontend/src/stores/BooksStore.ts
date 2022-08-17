import { writable } from 'svelte/store'

export const otBookStore = writable<Array<[string, string]>>([])
export const ntBookStore = writable<Array<[string, string]>>([])
