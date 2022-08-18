import { writable, Writable } from 'svelte/store'

export const printOptimizationStore: Writable<boolean> = writable(false)
export const assemblyStrategyKindStore: Writable<string> = writable('')
