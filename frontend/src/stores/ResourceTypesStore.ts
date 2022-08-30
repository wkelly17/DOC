import { writable, Writable } from 'svelte/store'

export let lang0ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let lang1ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let resourceTypesCountStore: Writable<number> = writable<number>(0)
