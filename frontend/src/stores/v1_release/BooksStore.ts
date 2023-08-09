import { writable, Writable } from 'svelte/store'

export let otBookStore: Writable<Array<string>> = writable<Array<string>>([])
export let ntBookStore: Writable<Array<string>> = writable<Array<string>>([])
export let bookCountStore: Writable<number> = writable<number>(0)
