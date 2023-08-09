import { writable, Writable } from 'svelte/store'

export let lang0NameAndCodeStore: Writable<string> = writable('')
export let lang1NameAndCodeStore: Writable<string> = writable('')
export let lang0CodeStore: Writable<string> = writable('')
export let lang1CodeStore: Writable<string> = writable('')
export let lang0NameStore: Writable<string> = writable('')
export let lang1NameStore: Writable<string> = writable('')
export let langCountStore: Writable<number> = writable<number>(0)

export let langCodeAndNamesStore: Writable<Array<string>> = writable([])
