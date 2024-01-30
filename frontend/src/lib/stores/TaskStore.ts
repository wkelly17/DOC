import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

export let taskIdStore: Writable<string> = writable<string>('');
export let taskStateStore: Writable<string> = writable<string>('');
