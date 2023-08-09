import { writable, Writable } from 'svelte/store'

export let documentReadyStore: Writable<boolean> = writable(false)
export let errorStore: Writable<string | null> = writable(null)
export let resetValuesStore: Writable<boolean> = writable(false)
