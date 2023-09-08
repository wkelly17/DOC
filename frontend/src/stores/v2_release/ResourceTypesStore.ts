import { writable, Writable } from 'svelte/store'

export let resourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let lang0ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let lang1ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let resourceTypesCountStore: Writable<number> = writable<number>(0)
export let twResourceRequestedStore: Writable<boolean> = writable<boolean>(false)
